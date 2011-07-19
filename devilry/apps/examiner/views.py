from django.views.generic import TemplateView, View
from django.shortcuts import render

import restful


class MainView(TemplateView):
    template_name='examiner/main.django.html'

    def get_context_data(self):
        context = super(MainView, self).get_context_data()
        for restclsname in restful.__all__:
            context[restclsname] = getattr(restful, restclsname)
        context['restfulclasses'] = [getattr(restful, restclsname) for restclsname in restful.__all__]
        return context


class ShowDeliveryView(View):
    def get(self, request, deliveryid):
        return render(request,
                      'examiner/showdelivery.django.html',
                      {'RestfulSimplifiedDelivery': restful.RestfulSimplifiedDelivery,
                       'RestfulSimplifiedFileMeta': restful.RestfulSimplifiedFileMeta,
                       'RestfulSimplifiedStaticFeedback': restful.RestfulSimplifiedStaticFeedback,
                       'deliveryid': deliveryid})
