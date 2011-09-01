from tempfile import TemporaryFile, NamedTemporaryFile
from django.views.generic import (TemplateView, View)
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.core.servers.basehttp import FileWrapper
from datetime import datetime
import zipfile
import tarfile
from os import stat
from mimetypes import guess_type
from time import mktime
import json
from ..core.models import (Delivery, FileMeta,
                           Deadline, AssignmentGroup,
                           Candidate)

from devilry.utils.module import dump_all_into_dict
from devilry.utils.filewrapperwithexplicitclose import FileWrapperWithExplicitClose
import restful
from restful import (RestfulSimplifiedDelivery, RestfulSimplifiedFileMeta,
                     RestfulSimplifiedDeadline,
                     RestfulSimplifiedStaticFeedback,
                     RestfulSimplifiedAssignment, RestfulSimplifiedAssignmentGroup)

class MainView(TemplateView):
    template_name='student/main.django.html'

    def get_context_data(self):
        context = super(MainView, self).get_context_data()
        context['restfulapi'] = dump_all_into_dict(restful);
        return context


class AddDeliveryView(View):
    def get(self, request, assignmentgroupid):
        assignmentgroup = get_object_or_404(AssignmentGroup, id=assignmentgroupid)
        deadline = assignmentgroup.get_active_deadline()
        deadline_timestamp_milliseconds = mktime(deadline.deadline.timetuple()) + (deadline.deadline.microsecond/1000000)
        deadline_timestamp_milliseconds *= 1000
        return render(request, 'student/add-delivery.django.html',
                      {'RestfulSimplifiedDelivery': RestfulSimplifiedDelivery,
                       'RestfulSimplifiedDeadline': RestfulSimplifiedDeadline,
                       'RestfulSimplifiedFileMeta': RestfulSimplifiedFileMeta,
                       'RestfulSimplifiedStaticFeedback': RestfulSimplifiedStaticFeedback,
                       'assignmentgroupid': assignmentgroupid,
                       'deadlineid': deadline.id,
                       'deadline_timestamp_milliseconds': deadline_timestamp_milliseconds,
                       'RestfulSimplifiedAssignment': RestfulSimplifiedAssignment,
                       'RestfulSimplifiedAssignmentGroup': RestfulSimplifiedAssignmentGroup}
                      )

class ShowDeliveryView(View):
    def get(self, request, deliveryid):
        return render(request, 'student/show-delivery.django.html',
                      {'RestfulSimplifiedDelivery': RestfulSimplifiedDelivery,
                       'RestfulSimplifiedFileMeta': RestfulSimplifiedFileMeta,
                       'RestfulSimplifiedStaticFeedback': RestfulSimplifiedStaticFeedback,
                       'deliveryid': deliveryid,
                       'RestfulSimplifiedAssignment': RestfulSimplifiedAssignment}
                      )

class FileUploadView(View):
    def post(self, request, assignmentgroupid):
        assignment_group_obj = get_object_or_404(AssignmentGroup, id=assignmentgroupid)
        deadlineid = assignment_group_obj.get_active_deadline().id
        deadline_obj = get_object_or_404(Deadline, id=deadlineid)
        logged_in_user = request.user
        deliveryid = request.POST['deliveryid']

        # Allow administrators and candidates on the group
        if not assignment_group_obj.can_save(logged_in_user):
            if not assignment_group_obj.is_candidate(logged_in_user):
                return HttpResponseForbidden()

        # Only allowed to add on open groups
        if not assignment_group_obj.can_add_deliveries():
            return HttpResponseForbidden()

        if 'uploaded_file' in request.FILES:
            #TODO Use simplified abstracted models
            uploaded_file = request.FILES['uploaded_file']
            uploaded_file_name = uploaded_file.name

            delivery = get_object_or_404(Delivery, id=deliveryid)
            delivery.add_file(uploaded_file_name, uploaded_file.chunks())
            delivery.full_clean()
            delivery.save()

            json_dict = {'success' : 'true', 'file':uploaded_file_name, 'deliveryid':delivery.id}
            json_result = json.dumps(json_dict)

            return HttpResponse(json_result)
        else:
            json_result = json.dumps({'success': 'false'})
            return HttpResponse(json_result)



class AssignmentGroupView(View):
    def get(self, request, assignmentgroupid):
        context = {'objectid': assignmentgroupid,
                   'restfulapi': dump_all_into_dict(restful)}
        return render(request,
                      'student/assignmentgroupview.django.html',
                       context)



class FileDownloadView(View):

    def get(self, request, filemetaid):    
        filemeta = get_object_or_404(FileMeta, id=filemetaid)
        assignment_group = filemeta.delivery.deadline.assignment_group
        if not (assignment_group.is_candidate(request.user) \
                    or assignment_group.is_examiner(request.user) \
                    or request.user.is_superuser \
                    or assignment_group.parentnode.is_admin(request.user)):
            return HttpResponseForbidden("Forbidden")
        
        # TODO: make this work on any storage backend
        response = HttpResponse(FileWrapper(filemeta.deliverystore.read_open(filemeta)),
                                content_type=guess_type(filemeta.filename))
        response['Content-Disposition'] = "attachment; filename=%s" % \
            filemeta.filename.encode("ascii", 'replace')
        response['Content-Length'] = filemeta.size

        return response


class CompressedFileDownloadView(View):

    def get(self, request, deliveryid):
        delivery = get_object_or_404(Delivery, id=deliveryid)
        zip_file_name = str(delivery.delivered_by) + ".zip"

        tempfile = NamedTemporaryFile()
        zip_file = zipfile.ZipFile(tempfile, 'w');

        for filemeta in delivery.filemetas.all():
            file_content = filemeta.deliverystore.read_open(filemeta)
            zip_file.write(file_content.name, filemeta.filename)
        zip_file.close()

        tempfile.seek(0)
        response = HttpResponse(FileWrapperWithExplicitClose(tempfile),
                                content_type="application/zip")
        response['Content-Disposition'] = "attachment; filename=%s" % \
            zip_file_name.encode("ascii", 'replace')
        response['Content-Length'] = stat(tempfile.name).st_size
        return response

class TarFileDownloadView(View):

    def get(self, request, deliveryid):
        delivery = get_object_or_404(Delivery, id=deliveryid)
        tar_file_name = str(request.user) + ".tar.gz"

        tempfile = TemporaryFile()
        tar_file = tarfile.open(tempfile.name, 'w');

        for filemeta in delivery.filemetas.all():
            file_content = filemeta.deliverystore.read_open(filemeta)
            tar_file.write(file_content.name, filemeta.filename)
        tar_file.close()

        tempfile.seek(0)
        response = HttpResponse(FileWrapperWithExplicitClose(tempfile),
                                content_type=guess_type(tar_file_name))
        response['Content-Disposition'] = "attachment; filename=%s" % \
            tar_file_name.encode("ascii", 'replace')
        response['Content-Length'] = stat(tempfile.name).st_size
        return response        
