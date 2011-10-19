from django.views.generic import TemplateView
from django.shortcuts import render

from devilry.apps.administrator import restful


class AdminStats(TemplateView):
    def get(self, request, periodid):

        context = {'periodid': periodid}
        context['RestfulSimplifiedRelatedStudent'] = restful.RestfulSimplifiedRelatedStudent
        context['RestfulSimplifiedRelatedStudentKeyValue'] = restful.RestfulSimplifiedRelatedStudentKeyValue
        context['RestfulSimplifiedPeriod'] = restful.RestfulSimplifiedPeriod
        context['RestfulSimplifiedAssignment'] = restful.RestfulSimplifiedAssignment
        context['RestfulSimplifiedAssignmentGroup'] = restful.RestfulSimplifiedAssignmentGroup
        return render(request,
                      'statistics/adminstats.django.js',
                       context) 
