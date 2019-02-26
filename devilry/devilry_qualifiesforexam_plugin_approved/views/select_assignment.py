# -*- coding: utf-8 -*-


# Devilry imports
from devilry.devilry_qualifiesforexam.views.plugin_base_views import base_multiselect_view
from devilry.devilry_qualifiesforexam.views.plugin_base_views.base_multiselect_view import \
    SelectableQualificationItemValue, SelectedQualificationItem
from devilry.devilry_qualifiesforexam_plugin_approved import resultscollector
from devilry.devilry_qualifiesforexam.views import plugin_mixin


class SelectedAssignmentItem(SelectedQualificationItem):
    def get_title(self):
        return self.value.long_name


class SelectableAssignmentItemValue(SelectableQualificationItemValue):
    selected_item_renderer_class = SelectedAssignmentItem

    def get_title(self):
        return self.value.long_name


class PluginSelectAssignmentsView(base_multiselect_view.QualificationItemListView, plugin_mixin.PluginMixin):
    plugintypeid = 'devilry_qualifiesforexam_plugin_approved.plugin_select_assignments'
    value_renderer_class = SelectableAssignmentItemValue

    def get_period_result_collector_class(self):
        return resultscollector.PeriodResultSetCollector
