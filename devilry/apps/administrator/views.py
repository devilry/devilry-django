from django.conf.urls.defaults import url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, View
from django.shortcuts import render

import restful


class MainView(TemplateView):
    template_name='administrator/main.django.html'

    def get_context_data(self):
        context = super(MainView, self).get_context_data()
        for restclsname in restful.__all__:
            context[restclsname] = getattr(restful, restclsname)
        context['restfulclasses'] = [getattr(restful, restclsname) for restclsname in restful.__all__]
        return context


class RestfulSimplifiedView(View):
    template_name = None

    def __init__(self, template_name):
        self.template_name = template_name

    def get(self, request, **indata):
        for restclsname in restful.__all__:
            indata[restclsname] = getattr(restful, restclsname)
        return render(request,
                      self.template_name,
                      indata)

    @classmethod
    def as_url(cls, prefix, idargname, template_name):
        return url(r'^{0}/(?P<{1}>\d+)$'.format(prefix, idargname),
                           login_required(cls.as_view(template_name=template_name)))
