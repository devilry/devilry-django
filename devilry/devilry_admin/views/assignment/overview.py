from __future__ import unicode_literals

from django_cradmin import crapp
from django_cradmin.viewhelpers.detail import DetailRoleView

from devilry.apps.core import models as coremodels


class Overview(DetailRoleView):
    model = coremodels.Assignment
    context_object_name = "assignment"
    template_name = 'devilry_admin/assignment/overview.django.html'

    def get_context_data(self, **kwargs):
        assignment = self.get_object()
        context = super(Overview, self).get_context_data(**kwargs)
        context['assignmentgroups_count'] = assignment.assignmentgroups.count()
        context['candidates_count'] = coremodels.Candidate.objects.filter(
            assignment_group__parentnode=assignment).count()
        context['administrator_count'] = len(assignment.get_all_admins())
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', Overview.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
