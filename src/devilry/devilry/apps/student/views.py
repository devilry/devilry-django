from tempfile import NamedTemporaryFile
import zipfile
from os import stat
from mimetypes import guess_type
from time import mktime
import posixpath

from django.views.generic import (TemplateView, View)
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.core.servers.basehttp import FileWrapper
from django.db import IntegrityError

from devilry.apps.core.models import Delivery, FileMeta, Deadline, AssignmentGroup
from devilry.utils.module import dump_all_into_dict
from devilry.utils.filewrapperwithexplicitclose import FileWrapperWithExplicitClose
from devilry.restful.serializers import (serialize, SerializableResult,
                                         ErrorMsgSerializableResult,
                                         ForbiddenSerializableResult)
from devilry.restful.extjshacks import extjshacks

import restful
from restful import (RestfulSimplifiedDelivery, RestfulSimplifiedFileMeta,
                     RestfulSimplifiedStaticFeedback,
                     RestfulSimplifiedAssignment)



class MainView(TemplateView):
    template_name='student/main.django.js'

    def get_context_data(self):
        context = super(MainView, self).get_context_data()
        context['restfulapi'] = dump_all_into_dict(restful);
        return context


class AddDeliveryView(View):
    def get(self, request, assignmentgroupid):
        assignment_group = get_object_or_404(AssignmentGroup, id=assignmentgroupid)
        logged_in_user = request.user
        if not assignment_group.can_save(logged_in_user):
            if not assignment_group.is_candidate(logged_in_user):
                return HttpResponseForbidden()
        deadline = assignment_group.get_active_deadline()
        deadline_timestamp_milliseconds = mktime(deadline.deadline.timetuple()) + (deadline.deadline.microsecond/1000000)
        deadline_timestamp_milliseconds *= 1000
        return render(request, 'student/add-delivery.django.html',
                      {'restfulapi': dump_all_into_dict(restful),
                       'assignmentgroupid': assignmentgroupid,
                       'deadlineid': deadline.id,
                       'deadline_timestamp_milliseconds': deadline_timestamp_milliseconds}
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

    @extjshacks
    @serialize(content_type_override='text/html')
    def post(self, request, assignmentgroupid):
        assignment_group_obj = get_object_or_404(AssignmentGroup, id=assignmentgroupid)
        deadlineid = assignment_group_obj.get_active_deadline().id
        deadline_obj = get_object_or_404(Deadline, id=deadlineid)
        logged_in_user = request.user
        deliveryid = request.POST['deliveryid']

        # Allow administrators and candidates on the group
        if not assignment_group_obj.can_save(logged_in_user):
            if not assignment_group_obj.is_candidate(logged_in_user):
                return ForbiddenSerializableResult()

        # Only allowed to add on open groups
        if not assignment_group_obj.can_add_deliveries():
            return ForbiddenSerializableResult()

        if 'uploaded_file' in request.FILES:
            #TODO Use simplified abstracted models
            uploaded_file = request.FILES['uploaded_file']
            uploaded_file_name = uploaded_file.name

            delivery = get_object_or_404(Delivery, id=deliveryid)
            try:
                delivery.add_file(uploaded_file_name, uploaded_file.chunks())
            except IntegrityError, e:
                return ErrorMsgSerializableResult('Filename must be unique',
                                                  httpresponsecls=HttpResponseBadRequest)
            delivery.full_clean()
            delivery.save()
            json_dict = {'success': True, 'file':uploaded_file_name, 'deliveryid':delivery.id}
            return SerializableResult(json_dict)
        else:
            return SerializableResult({'success': False})



class AssignmentGroupView(View):
    def get(self, request, assignmentgroupid):
        context = {'objectid': assignmentgroupid,
                   'restfulapi': dump_all_into_dict(restful)}
        return render(request,
                      'student/assignmentgroupview.django.js',
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
                                content_type=guess_type(filemeta.filename)[0])
        response['Content-Disposition'] = "attachment; filename=%s" % \
            filemeta.filename.encode("ascii", 'replace')
        response['Content-Length'] = filemeta.size

        return response


class CompressedFileDownloadView(View):

    def get(self, request, deliveryid):
        delivery = get_object_or_404(Delivery, id=deliveryid)
        assignment_group = delivery.deadline.assignment_group
        if not (assignment_group.is_candidate(request.user) \
                    or assignment_group.is_examiner(request.user) \
                    or request.user.is_superuser \
                    or assignment_group.parentnode.is_admin(request.user)):
            return HttpResponseForbidden("Forbidden")
        dirname = '{}-{}-delivery{}'.format(
                assignment_group.parentnode.get_path(),
                assignment_group.get_candidates(separator='_'),
                delivery.number)
        zip_file_name = u'{}.zip'.format(dirname)

        tempfile = NamedTemporaryFile()
        zip_file = zipfile.ZipFile(tempfile, 'w');

        for filemeta in delivery.filemetas.all():
            file_content = filemeta.deliverystore.read_open(filemeta)
            zip_file.write(file_content.name, posixpath.join(dirname, filemeta.filename))
        zip_file.close()

        tempfile.seek(0)
        response = HttpResponse(FileWrapperWithExplicitClose(tempfile),
                                content_type="application/zip")
        response['Content-Disposition'] = "attachment; filename=%s" % \
            zip_file_name.encode("ascii", 'replace')
        response['Content-Length'] = stat(tempfile.name).st_size
        return response

# TODO: Check permissions
#class TarFileDownloadView(View):

    #def get(self, request, deliveryid):
        #delivery = get_object_or_404(Delivery, id=deliveryid)
        #tar_file_name = str(request.user) + ".tar.gz"

        #tempfile = TemporaryFile()
        #tar_file = tarfile.open(tempfile.name, 'w');

        #for filemeta in delivery.filemetas.all():
            #file_content = filemeta.deliverystore.read_open(filemeta)
            #tar_file.write(file_content.name, filemeta.filename)
        #tar_file.close()

        #tempfile.seek(0)
        #response = HttpResponse(FileWrapperWithExplicitClose(tempfile),
                                #content_type=guess_type(tar_file_name))
        #response['Content-Disposition'] = "attachment; filename=%s" % \
            #tar_file_name.encode("ascii", 'replace')
        #response['Content-Length'] = stat(tempfile.name).st_size
        #return response        
