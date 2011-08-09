from django.views.generic import (TemplateView, View)
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.core.servers.basehttp import FileWrapper
from datetime import datetime
import zipfile
from os import stat
from mimetypes import guess_type
import json
from ..core.models import (Delivery, FileMeta, 
                           Deadline, AssignmentGroup,
                           Candidate)

from devilry.utils.module import dump_all_into_dict
import restful
from restful import (RestfulSimplifiedDelivery, RestfulSimplifiedFileMeta,
                     RestfulSimplifiedStaticFeedback, RestfulSimplifiedAssignment)

class MainView(TemplateView):
    template_name='student/main.django.html'

    def get_context_data(self):
        context = super(MainView, self).get_context_data()
        for restclsname in restful.__all__:
            context[restclsname] = getattr(restful, restclsname)
        context['restfulclasses'] = [getattr(restful, restclsname) for restclsname in restful.__all__]

        #print restful.RestfulSimplifiedAssignment._meta.simplified._meta.model.objects.all()
        
        return context

class AddDeliveryView(View):
    def get(self, request, deliveryid):
        return render(request, 'student/add-delivery.django.html',
                      {'RestfulSimplifiedDelivery': RestfulSimplifiedDelivery,
                       'RestfulSimplifiedFileMeta': RestfulSimplifiedFileMeta,
                       'RestfulSimplifiedStaticFeedback': RestfulSimplifiedStaticFeedback,
                       'deadlineid': deliveryid,
                       'RestfulSimplifiedAssignment': RestfulSimplifiedAssignment}
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

    def get(self, request, deadlineid):
        print "# FileUploadView GET-method #"
        print "#", deadlineid, "#"
        
        deadline_obj = get_object_or_404(Deadline, id=deadlineid)
        assignment_group_obj = get_object_or_404(AssignmentGroup, id=deadline_obj.assignment_group.id)
        logged_in_user = request.user        
        candidate = get_object_or_404(Candidate, student=logged_in_user, assignment_group=assignment_group_obj)
                
        delivery = Delivery()
        delivery.time_of_delivery = datetime.now()
        delivery.delivered_by = candidate
        delivery.succesful = False
        deadline_obj.deliveries.add(delivery)
        delivery.save()
        
        json_dict = {'success' : 'true', 'deliveryid' : delivery.id}
        json_result = json.dumps(json_dict)
        return HttpResponse(json_result)

    def post(self, request, deadlineid):
        print "#", deadlineid, "#"
        print "#", request.user, "#"
        print "#", request.POST['deliveryid'], "#"

        deadline_obj = get_object_or_404(Deadline, id=deadlineid)
        assignment_group_obj = get_object_or_404(AssignmentGroup, id=deadline_obj.assignment_group.id)
        logged_in_user = request.user
        deliveryid = request.POST['deliveryid']

        if not assignment_group_obj.is_candidate(logged_in_user):
            #TODO return Json
            return HttpResponseForbidden("Oh no rude boy! You're not the right guy")

        if not assignment_group_obj.can_add_deliveries():
            #TODO return Json
            return HttpResponseForbidden("Oh no rude boy! You're not allowed to deliver")

        
        if 'dendrofil' in request.FILES:
            
            #TODO Use simplified abstracted models
            uploaded_file = request.FILES['dendrofil']
            uploaded_file_name = uploaded_file.name

            delivery = get_object_or_404(Delivery, id=deliveryid)
            delivery.time_of_delivery = datetime.now()
            
            delivery.add_file(uploaded_file_name, uploaded_file.chunks())

            delivery.succesful= True
            delivery.full_clean()
            delivery.save()      
            
            json_dict = {'success' : 'true', 'file' : uploaded_file_name, 'deliveryid' : delivery.id}
            json_result = json.dumps(json_dict)
           
            return HttpResponse(json_result)

        else:

            json_result = json.dumps({'success': 'false', 'file': 'null'})
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
        print filemeta
        assignment_group = filemeta.delivery.deadline.assignment_group
        if not (assignment_group.is_candidate(request.user) \
                    or assignment_group.is_examiner(request.user) \
                    or request.user.is_superuser \
                    or assignment_group.parentnode.is_admin(request.user)):
            return http.HttpResponseForbidden("Forbidden")
        
        # TODO: make this work on any storage backend
        response = HttpResponse(FileWrapper(filemeta.deliverystore.read_open(filemeta)),
                                content_type=guess_type(filemeta.filename))
        response['Content-Disposition'] = "attachment; filename=%s" % \
            filemeta.filename.encode("ascii", 'replace')
        response['Content-Length'] = filemeta.size

        return response


from tempfile import TemporaryFile

class CompressedFileDownloadView(View):

    def get(self, request, deliveryid):
        delivery = get_object_or_404(Delivery, id=deliveryid)
        zip_file_name = str(request.user) + ".zip"

        tempfile = TemporaryFile()
        zip_file = zipfile.ZipFile(tempfile, 'w');

        for filemeta in delivery.filemetas.all():
            file_content = filemeta.deliverystore.read_open(filemeta)
            zip_file.write(file_content.name, filemeta.filename)
        zip_file.close()

        tempfile.seek(0)
        response = HttpResponse(FileWrapper(tempfile),
                                content_type=guess_type(zip_file_name))
        response['Content-Disposition'] = "attachment; filename=%s" % \
            zip_file_name.encode("ascii", 'replace')
        response['Content-Length'] = stat(zip_file_name).st_size
        return response
