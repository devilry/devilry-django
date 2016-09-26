# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Devilry imports
from devilry.devilry_qualifiesforexam.views import plugin_mixin
from devilry.devilry_qualifiesforexam.views.plugin_base_views import base_multiselect_view
from devilry.apps.core import models as core_models


class PluginForm(base_multiselect_view.SelectedQualificationForm):
    qualification_modelclass = core_models.Assignment
    invalid_qualification_item_message = 'Invalid qualification items was selected.'

    def __init__(self, *args, **kwargs):
        selectable_qualification_items_queryset = kwargs.pop('selectable_items_queryset')
        super(PluginForm, self).__init__(*args, **kwargs)
        self.fields['selected_items'].queryset = selectable_qualification_items_queryset


class PluginSelectAssignmentsView(base_multiselect_view.QualificationItemListView, plugin_mixin.PluginMixin):
    model = core_models.Assignment

    def get_queryset_for_role(self, role):
        queryset = super(PluginSelectAssignmentsView, self).get_queryset_for_role(role)
        queryset = queryset.filter(parentnode__id=role.id)
        return queryset

    def get_form_class(self):
        return PluginForm

    def get_inititially_selected_queryset(self):
        """
        Select all assignments as must be approved by default.
        The user can then deselect desired items.

        Returns:
            QuerySet: Assignments for the role.
        """
        return self.get_queryset_for_role(self.request.cradmin_role)
