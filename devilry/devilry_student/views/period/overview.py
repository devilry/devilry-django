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


class PeriodOverviewView(listbuilderview.FilterListMixin,
                         listbuilderview.View):
    model = coremodels.AssignmentGroup
    value_renderer_class = devilry_listbuilder.assignmentgroup.StudentItemValue
    frame_renderer_class = GroupItemFrame
    paginate_by = 15
    template_name = 'devilry_student/period/overview.django.html'

    def __get_assignment_id_to_assignment_map(self):
        assignmentqueryset = Assignment.objects\
            .filter_student_has_access(user=self.request.user)\
            .filter(parentnode=self.request.cradmin_role)\
            .select_related('parentnode__parentnode')\
            .prefetch_point_to_grade_map()
        assignment_id_to_assignment_map = {}
        for assignment in assignmentqueryset:
            assignment_id_to_assignment_map[assignment.id] = assignment
        return assignment_id_to_assignment_map

    def get_value_and_frame_renderer_kwargs(self):
        kwargs = super(PeriodOverviewView, self).get_value_and_frame_renderer_kwargs()
        kwargs.update({
            'assignment_id_to_assignment_map': self.__get_assignment_id_to_assignment_map(),
            'include_periodpath': False
        })
        return kwargs

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            crapp.INDEXVIEW_NAME,
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
        period = role
        return coremodels.AssignmentGroup.objects\
            .filter(parentnode__parentnode=period)\
            .filter_student_has_access(user=self.request.user)\
            .distinct()\
            .select_related(
                'parentnode',
                'cached_data__last_published_feedbackset',
                'cached_data__last_feedbackset',
                'cached_data__first_feedbackset',
            )\
            .order_by('-cached_data__last_feedbackset__deadline_datetime')

    def get_no_items_message(self):
        return pgettext_lazy('student period overview',
                             'No assignments.')

    def get_context_data(self, **kwargs):
        context = super(PeriodOverviewView, self).get_context_data(**kwargs)
        context['period'] = self.request.cradmin_role
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^(?P<filters_string>.+)?$$',
                  PeriodOverviewView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
    ]
