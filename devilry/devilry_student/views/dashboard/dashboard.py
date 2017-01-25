from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy, pgettext_lazy
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers import listfilter

from devilry.apps.core import models as coremodels
from devilry.apps.core.models import Assignment
from devilry.devilry_cradmin import devilry_listbuilder


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
            label=ugettext_lazy('Search'),
            label_is_screenreader_only=True,
            modelfields=[
                'parentnode__long_name',
                'parentnode__short_name',
                'parentnode__parentnode__long_name',
                'parentnode__parentnode__short_name',
                'parentnode__parentnode__parentnode__long_name',
                'parentnode__parentnode__parentnode__short_name',
            ]))

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
            .order_by('-parentnode__first_deadline', '-parentnode__publishing_time')\
            .prefetch_assignment_with_points_to_grade_map(
                assignmentqueryset=Assignment.objects.select_related('parentnode__parentnode'))

    def get_no_items_message(self):
        return pgettext_lazy('student dashboard',
                             'You have no active assignments. Use the button below to '
                             'browse inactive assignments and courses.')


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  DashboardView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  DashboardView.as_view(),
                  name='filter'),
    ]
