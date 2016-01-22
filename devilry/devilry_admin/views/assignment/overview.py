from __future__ import unicode_literals

from django_cradmin import crapp
from django_cradmin.viewhelpers.detail import DetailRoleView

from devilry.apps.core import models as coremodels
from devilry.apps.core.models import Examiner
from devilry.devilry_admin.views.assignment.anonymizationmode import AssignmentAnonymizationmodeUpdateView
from devilry.devilry_admin.views.assignment.gradingconfiguration import AssignmentGradingConfigurationUpdateView
from devilry.devilry_admin.views.assignment.long_and_shortname import AssignmentLongAndShortNameUpdateView
from devilry.devilry_admin.views.assignment.projectgroups import AssignmentProjectGroupUpdateView
from .first_deadline import AssignmentFirstDeadlineUpdateView
from .publishing_time import AssignmentPublishingTimeUpdateView, PublishNowRedirectView


class Overview(DetailRoleView):
    model = coremodels.Assignment
    context_object_name = "assignment"
    template_name = 'devilry_admin/assignment/overview.django.html'

    def get_candidates_count(self):
        return coremodels.Candidate.objects.filter(assignment_group__parentnode=self.assignment).count()

    def get_examiners_count(self):
        assignment = self.request.cradmin_role
        return Examiner.objects\
            .filter(assignmentgroup__parentnode=assignment)\
            .distinct('relatedexaminer__user').count()

    def get_assignmentgroups_count(self):
        return self.assignment.assignmentgroups.count()

    def dispatch(self, request, *args, **kwargs):
        self.assignment = self.get_object()
        return super(Overview, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context['assignmentgroups_count'] = self.get_assignmentgroups_count()
        context['candidates_count'] = self.get_assignmentgroups_count()
        context['examiners_count'] = self.get_examiners_count()
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', Overview.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^update_first_deadline/(?P<pk>\d+)$', AssignmentFirstDeadlineUpdateView.as_view(),
                  name="update_first_deadline"),
        crapp.Url(r'^update_publishing_time/(?P<pk>\d+)$', AssignmentPublishingTimeUpdateView.as_view(),
                  name="update_publishing_time"),
        crapp.Url(r'^update_anonymizationmode/(?P<pk>\d+)$', AssignmentAnonymizationmodeUpdateView.as_view(),
                  name="update_anonymizationmode"),
        crapp.Url(r'^update_projectgroup_settings/(?P<pk>\d+)$', AssignmentProjectGroupUpdateView.as_view(),
                  name="update_projectgroup_settings"),
        crapp.Url(r'^update_gradingconfiguration/(?P<pk>\d+)$', AssignmentGradingConfigurationUpdateView.as_view(),
                  name="update_gradingconfiguration"),
        crapp.Url(r'^update_assignment_short_and_long_name/(?P<pk>\d+)$', AssignmentLongAndShortNameUpdateView.as_view(),
                  name="update_assignment_short_and_long_name"),
        crapp.Url(r'^publish_assignment_now/(?P<pk>\d+)$', PublishNowRedirectView.as_view(),
                  name="publish_assignment_now")
    ]
