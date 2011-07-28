from django.views.generic import TemplateView, View
from django.shortcuts import render

from devilry.apps.gradeeditors.restful import examiner as gradeeditors_restful
import restful


def dump_all_into_dict(module):
    """ Dump ``module.__all__ into a dict, and return the dict. """
    dct = {}
    for clsname in module.__all__:
        dct[clsname] = getattr(module, clsname)
    return dct


class MainView(TemplateView):
    template_name='examiner/main.django.html'

    def get_context_data(self):
        context = super(MainView, self).get_context_data()
        for restclsname in restful.__all__:
            context[restclsname] = getattr(restful, restclsname)
        context['restfulclasses'] = [getattr(restful, restclsname) for restclsname in restful.__all__]
        return context


class AssignmentGroupView(View):
    def get(self, request, assignmentgroupid):
        context = {'objectid': assignmentgroupid,
                   'restfulapi': dump_all_into_dict(restful),
                   'gradeeditors': dump_all_into_dict(gradeeditors_restful)
                  }
        return render(request,
                      'examiner/assignmentgroupview.django.html',
                       context)
