# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Devilry imports
from devilry.devilry_qualifiesforexam.views.plugin_base_views import base_multiselect_view
from devilry.devilry_qualifiesforexam_plugin_approved import resultscollector
from devilry.devilry_qualifiesforexam.views import plugin_mixin


class PluginSelectAssignmentsView(base_multiselect_view.QualificationItemListView, plugin_mixin.PluginMixin):
    plugintypeid = 'devilry_qualifiesforexam_plugin_approved.plugin_select_assignments'

    def get_period_result_collector_class(self):
        return resultscollector.PeriodResultSetCollector
