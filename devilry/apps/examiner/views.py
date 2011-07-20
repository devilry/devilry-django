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


class AssignmentGroupView(View):
    def get(self, request, assignmentgroupid):
        indata = {'assignmentgroupid': assignmentgroupid }
        for restclsname in restful.__all__:
            indata[restclsname] = getattr(restful, restclsname)
        return render(request,
                      'examiner/assignmentgroupview.django.html',
                       indata)
