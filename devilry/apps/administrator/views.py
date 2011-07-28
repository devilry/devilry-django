from django.conf.urls.defaults import url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, View
from django.shortcuts import render

from devilry.apps.gradeeditors.restful import administrator as gradeeditors_restful
import restful

def add_restfulapi_to_context(context):
    restfuldct = {}
    for restclsname in restful.__all__:
        restfuldct[restclsname] = getattr(restful, restclsname)
    context['restfulapi'] = restfuldct



class MainView(TemplateView):
    template_name='administrator/main.django.html'

    def get_context_data(self):
        context = super(MainView, self).get_context_data()
        add_restfulapi_to_context(context)
        return context


class RestfulSimplifiedView(View):
    template_name = None

    def __init__(self, template_name):
        self.template_name = template_name

    def edit_context(self, context):
        pass

    def get(self, request, **indata):
        context = indata
        add_restfulapi_to_context(context)
        self.edit_context(context)
        return render(request,
                      self.template_name,
                      context)

    @classmethod
    def as_url(cls, prefix, template_name):
        return url(r'^{0}/view/(?P<objectid>\d+)$'.format(prefix),
                           login_required(cls.as_view(template_name=template_name)))


class RestfulSimplifiedAssignmentGroupView(RestfulSimplifiedView):
    def edit_context(self, context):
        restfuldct = {}
        for restclsname in gradeeditors_restful.__all__:
            restfuldct[restclsname] = getattr(gradeeditors_restful, restclsname)
        context['gradeeditors'] = restfuldct
