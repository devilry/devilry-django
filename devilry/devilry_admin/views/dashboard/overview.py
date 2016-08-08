from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin.devilry_listbuilder.period import AdminItemValue
from django.db import models
from itertools import groupby

from django.utils.translation import ugettext
from django.views.generic import TemplateView
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers import listfilter
from django_cradmin.viewhelpers import listbuilder
from devilry.devilry_admin.listbuilder import admindashboard_subject_listbuilder
from devilry.apps.core import models as coremodels

from devilry.apps.core.models import Period, Subject
from devilry.devilry_account.models import SubjectPermissionGroup, PeriodPermissionGroup

# class Overview(TemplateView):
#     template_name = 'devilry_admin/dashboard/overview.django.html'
#
#     def __get_all_subjects_where_user_is_subjectadmin(self):
#         return Subject.objects.filter_user_is_admin(user=self.request.user)\
#             .order_by('long_name')\
#             .distinct()
#
#     def __get_all_periods_where_user_is_subjectadmin_or_periodadmin(self):
#         groups = []
#         periods = Period.objects.filter_user_is_admin(user=self.request.user)\
#             .select_related('parentnode')\
#             .order_by('short_name', 'parentnode__long_name')\
#             .distinct()
#         for key, items in groupby(periods, lambda period: period.short_name):
#             groups.append(list(items))
#         return groups
#
#     def get_context_data(self, **kwargs):
#         context = super(Overview, self).get_context_data(**kwargs)
#         context['subjects_where_user_is_subjectadmin'] = \
#             self.__get_all_subjects_where_user_is_subjectadmin()
#         context['periods_where_user_is_subjectadmin_or_periodadmin'] = \
#             self.__get_all_periods_where_user_is_subjectadmin_or_periodadmin()
#         return context
from django_cradmin.viewhelpers.listbuilder.itemvalue import TitleDescription


class SubjectItemFrame(devilry_listbuilder.common.GoForwardLinkItemFrame):
    """
    An item frame for the list of subjects in the Administrator Dashboard Overview
    """
    valuealias = 'subject'

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_subjectadmin',
            appname='overview',
            roleid=self.subject.id,
            viewname=crapp.INDEXVIEW_NAME
        )

    def get_extra_css_classes_list(self):
        return ['devilry-admin-dashboard-overview-subjectitemframe']


class OrderSubjectFilter(listfilter.django.single.select.AbstractOrderBy):
    def get_ordering_options(self):
        return [
            ('', {  # This will be the default sort order
                'label': 'Short Name',
                'order_by': ['short_name'],
            }),
            ('short_name_descending', {
                'label': 'Short Name (descending)',
                'order_by': ['-short_name'],
            }),
        ]


class OverviewSubjectListView(listbuilderview.FilterListMixin, listbuilderview.View):
    model = coremodels.Subject
    template_name = 'devilry_admin/dashboard/overview.django.html'
    frame_renderer_class = SubjectItemFrame
    value_renderer_class = devilry_listbuilder.subject.AdminItemValue

    def get_pageheading(self):
        return ugettext("Administrator dashboard")

    def get_pagetitle(self):
        return self.get_pageheading()

    def __get_all_subjects_where_user_is_subjectadmin(self):
        return Subject.objects.filter_user_is_admin(user=self.request.user) \
            .order_by('long_name') \
            .distinct()

    def __get_all_periods_where_user_is_subjectadmin_or_periodadmin(self):
        groups = []
        periods = Period.objects.filter_user_is_admin(user=self.request.user) \
            .select_related('parentnode') \
            .order_by('short_name', 'parentnode__long_name') \
            .distinct()
        for key, items in groupby(periods, lambda period: period.short_name):
            groups.append(list(items))
        return groups

    def add_filterlist_items(self, filterlist):
        """
        Add the filters to the filterlist.
        """
        filterlist.append(listfilter.django.single.textinput.Search(
            slug='search',
            label='Search',
            label_is_screenreader_only=True,
            modelfields=['long_name']))
        filterlist.append(OrderSubjectFilter(
            slug='short_name', label='Short name'))

    def get_filterlist_url(self, filters_string):
        """
        This is used by the filterlist to create URLs.
        """
        return self.request.cradmin_app.reverse_appurl(
            'filter', kwargs={'filters_string': filters_string})

    def get_unfiltered_queryset_for_role(self, site):
        """
        Create the queryset, and apply the filters from the filterlist.
        """
        # Return Subjects where the user can be admin on Subject and or admin on a Period within a Subject
        return coremodels.Subject.objects.filter_user_is_admin_for_any_periods_within_subject(self.request.user).\
            prefetch_active_period_objects()

    def get_context_data(self, **kwargs):
        context = super(OverviewSubjectListView, self).get_context_data(**kwargs)
        context['subjects_where_user_is_subjectadmin'] = \
            self.__get_all_subjects_where_user_is_subjectadmin()
        context['periods_where_user_is_subjectadmin_or_periodadmin'] = \
            self.__get_all_periods_where_user_is_subjectadmin_or_periodadmin()
        return context

class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', OverviewSubjectListView.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(
            r'^filter/(?P<filters_string>.+)?$',
            OverviewSubjectListView.as_view(),
            name='filter'),
    ]
