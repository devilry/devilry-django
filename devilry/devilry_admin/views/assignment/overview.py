from __future__ import unicode_literals

from django_cradmin import crapp
from django_cradmin.viewhelpers.detail import DetailRoleView

from devilry.apps.core import models as coremodels
from devilry.apps.core.models import Assignment
from devilry.apps.core.models import Examiner
from devilry.apps.core.models import RelatedExaminer
from devilry.apps.core.models import RelatedStudent
from devilry.devilry_admin.views.assignment.anonymizationmode import AssignmentAnonymizationmodeUpdateView
from devilry.devilry_admin.views.assignment.gradingconfiguration import AssignmentGradingConfigurationUpdateView
from devilry.devilry_admin.views.assignment.long_and_shortname import AssignmentLongAndShortNameUpdateView
from devilry.devilry_admin.views.assignment.projectgroups import AssignmentProjectGroupUpdateView
from .first_deadline import AssignmentFirstDeadlineUpdateView
from .publishing_time import AssignmentPublishingTimeUpdateView, PublishNowRedirectView


class Overview(DetailRoleView):
    model = coremodels.Assignment
    template_name = 'devilry_admin/assignment/overview.django.html'

    def get_candidates_count(self):
        return coremodels.Candidate.objects\
            .filter(assignment_group__parentnode=self.assignment)\
            .count()

    def get_examiners_count(self):
        return Examiner.objects\
            .filter(assignmentgroup__parentnode=self.assignment)\
            .distinct('relatedexaminer__user').count()

    def get_assignmentgroups_count(self):
        return self.assignment.assignmentgroups.count()

    def get_related_students_count(self):
        return RelatedStudent.objects\
            .filter(period=self.assignment.period)\
            .distinct('user').count()

    def get_related_examiners_count(self):
        return RelatedExaminer.objects\
            .filter(period=self.assignment.period)\
            .distinct('user').count()

    def show_info_box(self, assignment, candidates_count, examiners_count,
                      relatedstudents_count, relatedexaminers_count):
        return (candidates_count == 0 or
                examiners_count == 0 or
                not assignment.is_published or
                relatedstudents_count > candidates_count or
                relatedexaminers_count > examiners_count or
                relatedexaminers_count == 0 or
                relatedstudents_count == 0)

    @property
    def assignment(self):
        if not hasattr(self, '_assignment'):
            queryset = Assignment.objects\
                .filter(id=self.request.cradmin_role.id)\
                .prefetch_point_to_grade_map()
            self._assignment = queryset.get()
        return self._assignment

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context['assignmentgroups_count'] = self.get_assignmentgroups_count()
        context['candidates_count'] = self.get_candidates_count()
        context['examiners_count'] = self.get_examiners_count()
        context['assignment'] = self.assignment
        context['relatedstudents_count'] = self.get_related_students_count()
        context['relatedexaminers_count'] = self.get_related_examiners_count()
        context['show_info_box'] = self.show_info_box(
            context['assignment'],
            context['candidates_count'],
            context['examiners_count'],
            context['relatedstudents_count'],
            context['relatedexaminers_count'])
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', Overview.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^update_assignment_short_and_long_name/(?P<pk>\d+)$', AssignmentLongAndShortNameUpdateView.as_view(),
                  name="update_assignment_short_and_long_name"),
        crapp.Url(r'^update_publishing_time/(?P<pk>\d+)$', AssignmentPublishingTimeUpdateView.as_view(),
                  name="update_publishing_time"),
        crapp.Url(r'^publish_assignment_now/(?P<pk>\d+)$', PublishNowRedirectView.as_view(),
                  name="publish_assignment_now"),
        crapp.Url(r'^update_first_deadline/(?P<pk>\d+)$', AssignmentFirstDeadlineUpdateView.as_view(),
                  name="update_first_deadline"),
        crapp.Url(r'^update_gradingconfiguration/(?P<pk>\d+)$', AssignmentGradingConfigurationUpdateView.as_view(),
                  name="update_gradingconfiguration"),
        crapp.Url(r'^update_projectgroup_settings/(?P<pk>\d+)$', AssignmentProjectGroupUpdateView.as_view(),
                  name="update_projectgroup_settings"),
        crapp.Url(r'^update_anonymizationmode/(?P<pk>\d+)$', AssignmentAnonymizationmodeUpdateView.as_view(),
                  name="update_anonymizationmode"),
    ]
