from django.views.generic import TemplateView, View
from django.shortcuts import render

from devilry.apps.gradeeditors.restful import examiner as gradeeditors_restful
from devilry.utils.module import dump_all_into_dict
import restful


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

class AssignmentView(View):
    def get(self, request, assignmentid):
        context = {'assignmentid': assignmentid,
                   'restfulapi': dump_all_into_dict(restful),
                   'gradeeditors': dump_all_into_dict(gradeeditors_restful)
                  }
        return render(request,
                      'examiner/assignment.django.html',
                       context) 
