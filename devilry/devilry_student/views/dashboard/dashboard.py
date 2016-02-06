from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy, pgettext_lazy
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url
from django_cradmin.viewhelpers import listbuilder
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers import listfilter

from devilry.apps.core import models as coremodels
from devilry.devilry_cradmin import devilry_listfilter
from devilry.devilry_cradmin import devilry_listbuilder


class GroupItemValue(listbuilder.itemvalue.TitleDescription):
    valuealias = 'group'

    def get_title(self):
        return u'{} - {}'.format(self.group.period.get_path(), self.group.assignment.long_name)

    def get_description(self):
        pass
        # if self.group.waiting_for_feedback_count > 0:
        #     return ugettext_lazy('%(waiting_for_feedback_count)s waiting for feedback') % {
        #         'waiting_for_feedback_count': self.group.waiting_for_feedback_count
        #     }
        # else:
        #     return ugettext_lazy('Nobody waiting for feedback')

    def get_extra_css_classes_list(self):
        css_classes = ['devilry-student-listbuilder-grouplist-itemvalue']
        # if self.group.waiting_for_feedback_count > 0:
        #     css_classes.append('devilry-django-cradmin-listbuilder-itemvalue-titledescription-description-warning')
        # else:
        #     css_classes.append('devilry-django-cradmin-listbuilder-itemvalue-titledescription-description-muted')
        return css_classes


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
    value_renderer_class = GroupItemValue
    frame_renderer_class = GroupItemFrame

    def get_filterlist_template_name(self):
        return 'devilry_student/dashboard/dashboard.django.html'

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
            .select_related('parentnode', 'parentnode__parentnode')\
            .order_by('-parentnode__first_deadline', '-parentnode__publishing_time')


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  DashboardView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  DashboardView.as_view(),
                  name='filter'),
    ]
