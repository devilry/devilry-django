from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.functions import Lower, Concat
from django.utils.translation import ugettext

from django_cradmin.crinstance import reverse_cradmin_url
from django_cradmin.viewhelpers import listbuilderview

from devilry.apps.core import models as core_models
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter
from devilry.devilry_admin.views.dashboard.student_feedbackfeed_wizard import filters


class NonAnonymousGroupItemFrame(devilry_listbuilder.common.GoForwardLinkItemFrame):
    valuealias = 'group'

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_group_admin',
            roleid=self.group.id,
            appname='feedbackfeed'
        )

    def get_extra_css_classes_list(self):
        return ['devilry-admin-assignment-students-overview-group-linkframe']


class DepartmentAdminItemValueByAssignment(devilry_listbuilder.assignmentgroup.DepartmentAdminItemValue,
                                           devilry_listbuilder.assignmentgroup.NoMultiselectItemValue):
    template_name = 'devilry_admin/dashboard/student_feedbackfeed_wizard/group_by_assignment.django.html'

    @property
    def assignment(self):
        return self.group.assignment

    @property
    def period(self):
        return self.assignment.parentnode

    @property
    def subject(self):
        return self.period.parentnode

    def get_assignment(self):
        return self.group.assignment


class StudentAssignmentGroupListView(listbuilderview.FilterListMixin, listbuilderview.View):
    """
    """
    template_name = 'devilry_admin/dashboard/student_feedbackfeed_wizard/student_feedbackfeed_list_groups.django.html'
    model = core_models.AssignmentGroup
    frame_renderer_class = NonAnonymousGroupItemFrame
    filterview_name = 'student_group_filter'
    value_renderer_class = DepartmentAdminItemValueByAssignment
    paginate_by = 15

    def dispatch(self, request, *args, **kwargs):
        self.user_id = kwargs.get('user_id')
        self.assignment_queryset = core_models.Assignment.objects\
            .prefetch_point_to_grade_map()\
            .all()
        return super(StudentAssignmentGroupListView, self).dispatch(request, *args, **kwargs)

    @property
    def user_displayname(self):
        user = get_user_model().objects.get(id=self.user_id)
        return user.get_short_name()

    def get_pagetitle(self):
        return ugettext('Assignments for %(user_shortname)s') % {'user_shortname': self.user_displayname}

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            self.filterview_name,
            kwargs={
                'user_id': self.user_id,
                'filters_string': filters_string
            }
        )

    def add_filterlist_items(self, filterlist):
        filterlist.append(filters.SearchExtension())
        filterlist.append(filters.OrderByDeadline())
        filterlist.append(filters.IsActiveSemester())
        filterlist.append(devilry_listfilter.assignmentgroup.IsPassingGradeFilter())
        filterlist.append(devilry_listfilter.assignmentgroup.PointsFilter())

    def get_unfiltered_queryset_for_role(self, role):
        candidatequeryset = core_models.Candidate.objects \
            .select_related('relatedstudent__user') \
            .only(
                'candidate_id',
                'assignment_group',
                'relatedstudent__candidate_id',
                'relatedstudent__automatic_anonymous_id',
                'relatedstudent__active',
                'relatedstudent__user__shortname',
                'relatedstudent__user__fullname',
            ) \
            .order_by(
            Lower(Concat('relatedstudent__user__fullname',
                         'relatedstudent__user__shortname')))
        examinerqueryset = core_models.Examiner.objects \
            .select_related('relatedexaminer__user') \
            .only(
                'relatedexaminer',
                'assignmentgroup',
                'relatedexaminer__automatic_anonymous_id',
                'relatedexaminer__user__shortname',
                'relatedexaminer__active',
                'relatedexaminer__user__fullname',
            ) \
            .order_by(
            Lower(Concat('relatedexaminer__user__fullname',
                         'relatedexaminer__user__shortname')))
        candidates_ids_for_user = candidatequeryset.filter(
            relatedstudent__user_id=self.user_id)\
            .values_list('assignment_group_id', flat=True)
        queryset = core_models.AssignmentGroup.objects \
            .select_related('cached_data__last_published_feedbackset',
                            'cached_data__last_feedbackset',
                            'cached_data__first_feedbackset',
                            'parentnode', 'parentnode__parentnode', 'parentnode__parentnode__parentnode')\
            .filter_user_is_admin(user=self.request.user)\
            .filter(id__in=candidates_ids_for_user) \
            .prefetch_related(
            models.Prefetch('candidates',
                            queryset=candidatequeryset)) \
            .prefetch_related(
            models.Prefetch('examiners',
                            queryset=examinerqueryset)) \
            .annotate_with_is_waiting_for_feedback_count() \
            .annotate_with_is_waiting_for_deliveries_count() \
            .annotate_with_is_corrected_count() \
            .distinct()
        return queryset
