from django.conf.urls.defaults import url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, View
from django.shortcuts import render

from devilry.utils.module import dump_all_into_dict
from devilry.apps.gradeeditors.restful import administrator as gradeeditors_restful
import restful


class MainView(TemplateView):
    template_name='administrator/main.django.html'

    def get_context_data(self):
        context = super(MainView, self).get_context_data()
        context['restfulapi'] = dump_all_into_dict(restful);
        return context


class RestfulSimplifiedView(View):
    template_name = None

    def __init__(self, template_name):
        self.template_name = template_name

    def edit_context(self, context):
        pass

    def get(self, request, **indata):
        context = indata
        context['restfulapi'] = dump_all_into_dict(restful);
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
        context['restfulapi'] = dump_all_into_dict(restful);
        context['gradeeditors'] = dump_all_into_dict(gradeeditors_restful);
