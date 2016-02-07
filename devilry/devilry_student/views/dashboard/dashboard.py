from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy, pgettext_lazy
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers import listfilter

from devilry.apps.core import models as coremodels
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
    model = coremodels.Assignment
    value_renderer_class = devilry_listbuilder.assignmentgroup.StudentItemValue
    frame_renderer_class = GroupItemFrame
    template_name = 'devilry_student/dashboard/dashboard.django.html'

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
            .select_related('parentnode__parentnode__parentnode')\
            .annotate_with_grading_points()\
            .annotate_with_is_waiting_for_feedback()\
            .annotate_with_is_waiting_for_deliveries()\
            .annotate_with_is_corrected()\
            .annotate_with_number_of_commentfiles_from_students()\
            .annotate_with_number_of_groupcomments_from_students()\
            .annotate_with_number_of_groupcomments_from_examiners()\
            .annotate_with_number_of_imageannotationcomments_from_students()\
            .annotate_with_number_of_imageannotationcomments_from_examiners()\
            .distinct()\
            .order_by('-parentnode__first_deadline', '-parentnode__publishing_time')

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
