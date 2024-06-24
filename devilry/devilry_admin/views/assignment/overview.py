

from cradmin_legacy import crapp
from cradmin_legacy.viewhelpers.detail import DetailRoleView

from devilry.apps.core import models as coremodels
from devilry.apps.core.models import Assignment, Candidate, AssignmentGroup
from devilry.apps.core.models import Examiner
from devilry.apps.core.models import RelatedExaminer
from devilry.apps.core.models import RelatedStudent
from devilry.devilry_account.models import SubjectPermissionGroup
from devilry.devilry_admin.views.assignment.anonymizationmode import AssignmentAnonymizationmodeUpdateView
from devilry.devilry_admin.views.assignment.deadline_handling import AssignmentDeadlineHandlingUpdateView
from devilry.devilry_admin.views.assignment.gradingconfiguration import AssignmentGradingConfigurationUpdateView
from devilry.devilry_admin.views.assignment.long_and_shortname import AssignmentLongAndShortNameUpdateView
from devilry.devilry_admin.views.assignment.projectgroups import AssignmentProjectGroupUpdateView
from devilry.devilry_admin.views.assignment.examiner_selfassign import AssignmentExaminerSelfAssignUpdateView
from .first_deadline import AssignmentFirstDeadlineUpdateView
from .publishing_time import AssignmentPublishingTimeUpdateView, PublishNowRedirectView


class Overview(DetailRoleView):
    model = coremodels.Assignment
    template_name = 'devilry_admin/assignment/overview.django.html'

    def get_candidates_count(self):
        return coremodels.Candidate.objects\
            .filter(assignment_group__parentnode=self.assignment)\
            .count()

    def get_distinct_examiners_count(self):
        """
        Get distinct examiners otherwise the same relatedexaminer assigned to multiple groups
        would be shown as multiple examiners.
        """
        return Examiner.objects\
            .filter(assignmentgroup__parentnode=self.assignment)\
            .distinct('relatedexaminer__user').count()

    def get_assignmentgroups_count(self):
        return self.assignment.assignmentgroups.count()

    def get_related_students_count(self):
        return RelatedStudent.objects\
            .filter(period=self.assignment.period, active=True)\
            .distinct('user').count()

    def get_related_examiners_count(self):
        return RelatedExaminer.objects\
            .filter(period=self.assignment.period, active=True)\
            .distinct('user').count()

    @property
    def assignment(self):
        if not hasattr(self, '_assignment'):
            queryset = Assignment.objects\
                .filter(id=self.request.cradmin_role.id)\
                .prefetch_point_to_grade_map()
            self._assignment = queryset.get()
        return self._assignment

    def get_user_is_subjectadmin_or_higher(self):
        return SubjectPermissionGroup.objects\
            .get_devilryrole_for_user_on_subject(
                user=self.request.user, subject=self.assignment.parentnode.parentnode) is not None

    def get_assignment_groups_without_any_examiners(self):
        return AssignmentGroup.objects.filter(parentnode=self.request.cradmin_role, examiners__isnull=True)

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context['assignmentgroups_count'] = self.get_assignmentgroups_count()
        context['candidates_count'] = self.get_candidates_count()
        context['examiners_count'] = self.get_distinct_examiners_count()
        context['assignment'] = self.assignment
        context['relatedstudents_count'] = self.get_related_students_count()
        context['relatedexaminers_count'] = self.get_related_examiners_count()
        context['user_is_subjectadmin_or_higher'] = self.get_user_is_subjectadmin_or_higher()
        context['students_without_examiners_exists'] = self.get_assignment_groups_without_any_examiners().exists()
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  Overview.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^update_assignment_short_and_long_name/(?P<pk>\d+)$',
                  AssignmentLongAndShortNameUpdateView.as_view(),
                  name="update_assignment_short_and_long_name"),

        crapp.Url(r'^update_publishing_time/(?P<pk>\d+)$',
                  AssignmentPublishingTimeUpdateView.as_view(),
                  name="update_publishing_time"),

        crapp.Url(r'^publish_assignment_now/(?P<pk>\d+)$',
                  PublishNowRedirectView.as_view(),
                  name="publish_assignment_now"),

        crapp.Url(r'^update_first_deadline/(?P<pk>\d+)$',
                  AssignmentFirstDeadlineUpdateView.as_view(),
                  name="update_first_deadline"),

        crapp.Url(r'^update_gradingconfiguration/(?P<pk>\d+)$',
                  AssignmentGradingConfigurationUpdateView.as_view(),
                  name="update_gradingconfiguration"),

        crapp.Url(r'^update_projectgroup_settings/(?P<pk>\d+)$',
                  AssignmentProjectGroupUpdateView.as_view(),
                  name="update_projectgroup_settings"),

        crapp.Url(r'^update_anonymizationmode/(?P<pk>\d+)$',
                  AssignmentAnonymizationmodeUpdateView.as_view(),
                  name="update_anonymizationmode"),

        crapp.Url(r'^update_deadlinehandling/(?P<pk>\d+)',
                  AssignmentDeadlineHandlingUpdateView.as_view(),
                  name='update_deadline_handling'),
        crapp.Url(f'^update_examiner_selfassign_settings/(?P<pk>\d+)',
                AssignmentExaminerSelfAssignUpdateView.as_view(),
                name='update_examiner_selfassign_settings')
    ]
