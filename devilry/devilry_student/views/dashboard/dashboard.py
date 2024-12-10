

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy, pgettext_lazy
from cradmin_legacy import crapp
from cradmin_legacy.crinstance import reverse_cradmin_url
from cradmin_legacy.viewhelpers import listbuilderview
from cradmin_legacy.viewhelpers import listfilter
from cradmin_legacy.viewhelpers.listbuilder.lists import RowList

from devilry.apps.core import models as coremodels
from devilry.apps.core.models import Assignment
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter


class GroupItemFrame(devilry_listbuilder.common.GoForwardLinkItemFrame):
    valuealias = 'group'

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_group_student',
            appname='feedbackfeed',
            roleid=self.group.id,
            viewname=crapp.INDEXVIEW_NAME,
        )

    def get_extra_css_classes_list(self):
        return ['devilry-student-listbuilder-grouplist-itemframe']


class DashboardView(listbuilderview.FilterListMixin,
                    listbuilderview.View):
    model = coremodels.AssignmentGroup
    value_renderer_class = devilry_listbuilder.assignmentgroup.StudentItemValue
    frame_renderer_class = GroupItemFrame
    paginate_by = 15
    template_name = 'devilry_student/dashboard/dashboard.django.html'

    def __get_assignment_id_to_assignment_map(self):
        assignmentqueryset = Assignment.objects\
            .filter_student_has_access(user=self.request.user)\
            .select_related('parentnode__parentnode')\
            .prefetch_point_to_grade_map()
        assignment_id_to_assignment_map = {}
        for assignment in assignmentqueryset:
            assignment_id_to_assignment_map[assignment.id] = assignment
        return assignment_id_to_assignment_map

    def __get_upcoming_assignments_as_groups(self):
        """
        Get upcoming assignments the next seven days from now.

        Returns:
            QuerySet: ``AssignmentGroup`` query set.
        """
        now = timezone.now()
        days_from_now = timezone.now() + timezone.timedelta(days=7)
        queryset = coremodels.AssignmentGroup.objects\
            .filter_student_has_access(user=self.request.user)\
            .filter_is_active()\
            .distinct()\
            .select_related(
                'parentnode',
                'cached_data__last_published_feedbackset',
                'cached_data__last_feedbackset',
                'cached_data__first_feedbackset') \
            .filter(
                cached_data__last_feedbackset__deadline_datetime__gte=now,
                cached_data__last_feedbackset__deadline_datetime__lte=days_from_now) \
            .order_by('cached_data__last_feedbackset__deadline_datetime')\
            .prefetch_assignment_with_points_to_grade_map(
                assignmentqueryset=Assignment.objects.select_related('parentnode__parentnode'))
        return queryset

    def __upcoming_assignments_list(self, upcoming_assignments_as_groups_queryset=None):
        """
        Get upcoming assignments as a ``Django CrAdmin`` row list renderable.
        """
        assignment_id_to_assignment_map = self.__get_assignment_id_to_assignment_map()
        kwargs = {'assignment_id_to_assignment_map': assignment_id_to_assignment_map}
        if not upcoming_assignments_as_groups_queryset:
            upcoming_assignments_as_groups_queryset = self.__get_upcoming_assignments_as_groups()
        return RowList.from_value_iterable(
            value_iterable=upcoming_assignments_as_groups_queryset,
            value_renderer_class=self.value_renderer_class,
            frame_renderer_class=self.frame_renderer_class,
            value_and_frame_renderer_kwargs=kwargs)

    def get_value_and_frame_renderer_kwargs(self):
        kwargs = super(DashboardView, self).get_value_and_frame_renderer_kwargs()
        kwargs.update({
            'assignment_id_to_assignment_map': self.__get_assignment_id_to_assignment_map()
        })
        return kwargs

    def get_pagetitle(self):
        return pgettext_lazy('student dashboard',
                             'Student dashboard')

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'filter',
            kwargs={'filters_string': filters_string})

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter.django.single.textinput.Search(
            slug='search',
            label=gettext_lazy('Search'),
            label_is_screenreader_only=True,
            modelfields=[
                'parentnode__long_name',
                'parentnode__short_name',
                'parentnode__parentnode__long_name',
                'parentnode__parentnode__short_name',
                'parentnode__parentnode__parentnode__long_name',
                'parentnode__parentnode__parentnode__short_name',
            ]))
        filterlist.append(devilry_listfilter.assignmentgroup.IsPassingGradeFilter())

    def get_unfiltered_queryset_for_role(self, role):
        return coremodels.AssignmentGroup.objects\
            .filter_student_has_access(user=self.request.user)\
            .filter_is_active()\
            .distinct()\
            .select_related(
                'parentnode',
                'cached_data__last_published_feedbackset',
                'cached_data__last_feedbackset',
                'cached_data__first_feedbackset',
            )\
            .order_by('-cached_data__last_feedbackset__deadline_datetime')\
            .prefetch_assignment_with_points_to_grade_map(
                assignmentqueryset=Assignment.objects.select_related('parentnode__parentnode'))

    def get_no_items_message(self):
        return pgettext_lazy('student dashboard',
                             'You have no active assignments. Use the button below to '
                             'browse inactive assignments and courses.')

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        upcoming_assignments_as_groups_queryset = self.__get_upcoming_assignments_as_groups()
        context['upcoming_assignments_count'] = upcoming_assignments_as_groups_queryset.count()
        context['upcoming_assignment_renderables'] = self.__upcoming_assignments_list(
            upcoming_assignments_as_groups_queryset=upcoming_assignments_as_groups_queryset
        )
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  DashboardView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  DashboardView.as_view(),
                  name='filter'),
    ]
