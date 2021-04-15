# -*- coding: utf-8 -*-


from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin.devilry_listbuilder.period import AdminItemValue
from django.db import models
from itertools import groupby

from django.utils.translation import gettext, gettext_lazy
from django.views.generic import TemplateView
from cradmin_legacy import crapp
from cradmin_legacy.crinstance import reverse_cradmin_url
from cradmin_legacy.viewhelpers import listbuilderview
from cradmin_legacy.viewhelpers import listfilter
from cradmin_legacy.viewhelpers import listbuilder
from devilry.devilry_admin.listbuilder import admindashboard_subject_listbuilder
from devilry.apps.core import models as coremodels

from devilry.apps.core.models import Period, Subject
from devilry.devilry_account.models import SubjectPermissionGroup, PeriodPermissionGroup
from devilry.devilry_cradmin.devilry_listfilter.utils import WithResultValueRenderable, RowListWithMatchResults


class SubjectItemFrame(devilry_listbuilder.common.GoForwardLinkItemFrame):
    """
    An item frame for the list of subjects in the Administrator Dashboard Overview
    """
    valuealias = 'subject'

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_subject_for_periodadmin',
            appname='subject_redirect',
            roleid=self.subject.id,
            viewname=crapp.INDEXVIEW_NAME
        )

    def get_extra_css_classes_list(self):
        return ['devilry-admin-dashboard-overview-subjectitemframe']


class OrderSubjectFilter(listfilter.django.single.select.AbstractOrderBy):
    def get_ordering_options(self):
        return [
            ('', {  # This will be the default sort order
                'label': gettext_lazy('Short Name'),
                'order_by': ['short_name'],
            }),
            ('short_name_descending', {
                'label': gettext_lazy('Short Name (descending)'),
                'order_by': ['-short_name'],
            }),
        ]


class SubjectListMatchResultRenderable(WithResultValueRenderable):
    def get_object_name_singular(self, num_matches):
        return gettext_lazy('course')

    def get_object_name_plural(self, num_matches):
        return gettext_lazy('courses')


class RowListBuilder(RowListWithMatchResults):
    match_result_value_renderable = SubjectListMatchResultRenderable


class OverviewSubjectListView(listbuilderview.FilterListMixin, listbuilderview.View):
    model = coremodels.Subject
    template_name = 'devilry_admin/dashboard/overview.django.html'
    listbuilder_class = RowListBuilder
    frame_renderer_class = SubjectItemFrame
    value_renderer_class = devilry_listbuilder.subject.AdminItemValue
    paginate_by = 50

    def get_pageheading(self):
        return gettext("Administrator dashboard")

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
            slug='short_name', label=gettext_lazy('Short name')))

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
        queryset = coremodels.Subject.objects\
            .filter_user_is_admin_for_any_periods_within_subject(self.request.user)\
            .prefetch_active_period_objects()

        # Set unfiltered count on self.
        self.num_total = queryset.count()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(OverviewSubjectListView, self).get_context_data(**kwargs)
        context['subjects_where_user_is_subjectadmin'] = \
            self.__get_all_subjects_where_user_is_subjectadmin()
        context['periods_where_user_is_subjectadmin_or_periodadmin'] = \
            self.__get_all_periods_where_user_is_subjectadmin_or_periodadmin()
        return context

    #
    # Add support for showing results on the top of the list.
    #
    def get_listbuilder_list_kwargs(self):
        kwargs = super(OverviewSubjectListView, self).get_listbuilder_list_kwargs()
        kwargs['num_matches'] = self.num_matches or 0
        kwargs['num_total'] = self.num_total or 0
        kwargs['page'] = self.request.GET.get('page', 1)
        return kwargs

    def get_queryset_for_role(self, role):
        queryset = super(OverviewSubjectListView, self).get_queryset_for_role(role=role)

        # Set filtered count on self.
        self.num_matches = queryset.count()
        return queryset

class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', OverviewSubjectListView.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(
            r'^filter/(?P<filters_string>.+)?$',
            OverviewSubjectListView.as_view(),
            name='filter'),
    ]
