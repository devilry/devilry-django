from django.views.generic import (TemplateView, View)
from django.shortcuts import render
from django.http import HttpResponse
import datetime

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

    def post(self, request, deliveryid):
        print "#", request.FILES['dendrofil'].size, "#"
        filen = request.FILES['dendrofil'].read()
        print filen
        print dir(filen)
        return HttpResponse("{success: true, file: null}")
                      
