from __future__ import unicode_literals

from django_cradmin import crapp
from django_cradmin.viewhelpers.detail import DetailRoleView

from devilry.apps.core import models as coremodels
from .first_deadline import AssignmentFirstDeadlineUpdateView


class Overview(DetailRoleView):
    model = coremodels.Assignment
    context_object_name = "assignment"
    template_name = 'devilry_admin/assignment/overview.django.html'

    def get_administrators_count(self):
        # len(self.assignment.get_all_admins()) is deprecated
        return 10

    def get_candidates_count(self):
        return coremodels.Candidate.objects.filter(assignment_group__parentnode=self.assignment).count()

    def get_examiners_count(self):
        examiners_count = 0
        for group in self.assignment.assignmentgroups.all():
            examiners_count += group.examiners.count()
        return examiners_count
    
    def get_assignmentgroups_count(self):
        return self.assignment.assignmentgroups.count()

    def dispatch(self, request, *args, **kwargs):
        self.assignment = self.get_object()
        return super(Overview, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context['assignmentgroups_count'] = self.get_assignmentgroups_count()
        context['candidates_count'] = self.get_assignmentgroups_count()
        context['administrator_count'] = self.get_administrators_count()
        context['examiners_count'] = self.get_examiners_count()
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', Overview.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^update/(?P<pk>\d+)$', AssignmentFirstDeadlineUpdateView.as_view(), name="update_first_deadline")
    ]
