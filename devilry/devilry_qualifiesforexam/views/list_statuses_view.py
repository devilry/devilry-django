# -*- coding: utf-8 -*-


# Django imports
from django.db import models

# CrAdmin imports
from django.utils.translation import gettext_lazy
from cradmin_legacy.viewhelpers import listbuilderview
from cradmin_legacy.viewhelpers import listbuilder
from cradmin_legacy.crinstance import reverse_cradmin_url
from cradmin_legacy.viewhelpers import listfilter


# Devilry imports
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_qualifiesforexam import models as status_models
from devilry.apps.core import models as core_models


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
            viewname='show-status',
            kwargs={
                'statusid': self.status.id
            }
        )

    def get_extra_css_classes_list(self):
        return ['devilry-qualifiesforexam-list-statuses-statusitemframe']


class OrderStatusFilter(listfilter.django.single.select.AbstractOrderBy):
    def get_ordering_options(self):
        return [
            ('status (ready)', {
                'label': gettext_lazy('Status (ready)'),
                'order_by': ['-status']
            }),
            ('status (not ready)', {
                'label': gettext_lazy('Status (not ready)'),
                'order_by': ['status']
            })
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
        filterlist.append(OrderStatusFilter(
            slug='orderby', label='Order by'))

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'filter', kwargs={'filters_string': filters_string})

    def get_unfiltered_queryset_for_role(self, role):
        period = self.request.cradmin_role
        period_queryset = core_models.Period.objects.prefetch_related(
            models.Prefetch(
                    'qualifiedforexams_status',
                    queryset=status_models.Status.objects.filter(period=period)
            )
        ).get(id=period.id)
        return period_queryset.qualifiedforexams_status.all()

    def get_no_items_message(self):
        return gettext_lazy('No status has been created for this period yet.')

    def get_context_data(self, **kwargs):
        context_data = super(ListStatusesView, self).get_context_data(**kwargs)
        context_data['headline'] = gettext_lazy('Status overview for %(what)s') % {'what': self.request.cradmin_role}
        context_data['help_text'] = gettext_lazy(
            'You can either choose a plugin to create a new status, or you can select a '
            'retracted status.'
        )
        return context_data
