from django.db import models
from itertools import groupby

from django.utils.translation import ugettext
from django.views.generic import TemplateView
from django_cradmin import crapp
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers import listfilter
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

    def get_pageheading(self):
        return ugettext("Administrator dashboard")

    def get_pagetitle(self):
        return self.get_pageheading()

    def __get_all_subjects_where_user_is_subjectadmin(self):
        return Subject.objects.filter_user_is_admin(user=self.request.user)\
            .order_by('long_name')\
            .distinct()

    def __get_all_periods_where_user_is_subjectadmin_or_periodadmin(self):
        groups = []
        periods = Period.objects.filter_user_is_admin(user=self.request.user)\
            .select_related('parentnode')\
            .order_by('short_name', 'parentnode__long_name')\
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
        return coremodels.Subject.objects.all()


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', OverviewSubjectListView.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(
                r'^filter/(?P<filters_string>.+)?$',
                OverviewSubjectListView.as_view(),
                name='filter'),
    ]
