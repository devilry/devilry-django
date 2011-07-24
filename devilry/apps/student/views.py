from django.views.generic import (TemplateView, View)
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from datetime import datetime
import json
from ..core.models import (Delivery, FileMeta, 
                           Deadline, AssignmentGroup,
                           Candidate)

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

class FileUploadView(View):
    # def get(self, request, deliveryid):
    #     return render(request, 'student/add-delivery.django.html',
    #                   {'RestfulSimplifiedDelivery': RestfulSimplifiedDelivery,
    #                    'RestfulSimplifiedFileMeta': RestfulSimplifiedFileMeta,
    #                    'RestfulSimplifiedStaticFeedback': RestfulSimplifiedStaticFeedback,
    #                    'deadlineid': deliveryid,
    #                    'RestfulSimplifiedAssignment': RestfulSimplifiedAssignment}
    #                   )

    def post(self, request, deadlineid):
        print "#", deadlineid, "#"
        print "#", request.user, "#"

        deadline_obj = get_object_or_404(Deadline, id=deadlineid)
        assignment_group_obj = get_object_or_404(AssignmentGroup, id=deadline_obj.assignment_group.id)
        logged_in_user = request.user
        candidate = get_object_or_404(Candidate, assignment_group=assignment_group_obj)

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

            delivery = Delivery()
            delivery.time_of_delivery = datetime.now()
            delivery.delivered_by = candidate
            delivery.succesful = False
            deadline_obj.deliveries.add(delivery)
            delivery.save()
            
            delivery.add_file(uploaded_file_name, uploaded_file.chunks())

            delivery.succesful= True
            delivery.full_clean()
            delivery.save()      
            
            json_dict = {'success' : 'true', 'file' : uploaded_file_name}
            json_result = json.dumps(json_dict)
           
            return HttpResponse(json_result)

        else:

            json_result = json.dumps({'success': 'false', 'file': 'null'})
            return HttpResponse(json_result)



class AssignmentGroupView(View):
    def get(self, request, assignmentgroupid):
        indata = {'assignmentgroupid': assignmentgroupid }
        for restclsname in restful.__all__:
            indata[restclsname] = getattr(restful, restclsname)
        return render(request,
                      'student/assignmentgroupview.django.html',
                       indata)
