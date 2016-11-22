# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# CrAdmin imports
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers import listbuilder
from django_cradmin.crinstance import reverse_cradmin_url
from django_cradmin.viewhelpers import listfilter


# Devilry imports
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_qualifiesforexam import models as status_models


class StatusItemValue(listbuilder.itemvalue.TitleDescription):
    """
    Base value class.
    """
    valuealias = 'status'
    template_name = 'devilry_qualifiesforexam/listbuilder/description.django.html'


class StatusItemFrame(devilry_listbuilder.common.GoForwardLinkItemFrame):
    valuealias = 'status'

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_admin_periodadmin',
            roleid=self.status.period.id,
            appname='qualifiesforexam',
            viewname='show-status'
        )

    def get_extra_css_classes_list(self):
        return ['devilry-qualifiesforexam-list-statuses-statusitemframe']


class OrderStatusFilter(listfilter.django.single.select.AbstractOrderBy):
    def get_ordering_options(self):
        return [
            ('', {
                'label': 'Created (descending)',
                'order_by': ['-createtime']
            }),
            ('created_ascending', {
                'label': 'Created (ascending)',
                'order_by': ['createtime']
            }),
        ]


class ListStatusesView(listbuilderview.FilterListMixin, listbuilderview.View):
    """
    View for listing statuses created for the period.

    This is the index view for the ``devilry_qualifiesforexam`` app and lists statuses created with the
    plugins. A link to the plugin selection page is also provided.
    """
    template_name = 'devilry_qualifiesforexam/list_statuses.django.html'
    model = status_models.Status
    frame_renderer_class = StatusItemFrame
    value_renderer_class = StatusItemValue

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter.django.single.textinput.Search(
            slug='search',
            label='Search',
            modelfields=['status'],
            label_is_screenreader_only=True
        ))
        filterlist.append(OrderStatusFilter(
            slug='orderby', label='Order by'))

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'filter', kwargs={'filters_string': filters_string})

    def get_unfiltered_queryset_for_role(self, role):
        period = self.request.cradmin_role
        return status_models.Status.objects.filter(period=period)

    def get_no_items_message(self):
        return 'No status has been created for this period yet.'

    def get_context_data(self, **kwargs):
        context_data = super(ListStatusesView, self).get_context_data(**kwargs)
        context_data['headline'] = 'Status overview for {}'.format(self.request.cradmin_role)
        context_data['help_text'] = 'You can either choose a plugin to create a new status, or you can select a ' \
                                    'retracted status.'
        return context_data
