# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django.http import HttpResponseRedirect

# Devilry imports
from devilry.devilry_qualifiesforexam.views import plugin_mixin
from devilry.devilry_qualifiesforexam.views.plugin_base_views import base_multiselect_view
from devilry.apps.core import models as core_models
from devilry.devilry_qualifiesforexam_plugin_approved import resultscollector


class PluginForm(base_multiselect_view.SelectedQualificationForm):
    qualification_modelclass = core_models.Assignment
    invalid_qualification_item_message = 'Invalid qualification items was selected.'

    def __init__(self, *args, **kwargs):
        selectable_qualification_items_queryset = kwargs.pop('selectable_items_queryset')
        super(PluginForm, self).__init__(*args, **kwargs)
        self.fields['selected_items'].queryset = selectable_qualification_items_queryset


class PluginSelectAssignmentsView(base_multiselect_view.QualificationItemListView, plugin_mixin.PluginMixin):
    model = core_models.Assignment
    plugintypeid = 'devilry_qualifiesforexam_plugin_approved.plugin_select_assignments'

    def get(self, request, *args, **kwargs):
        return super(PluginSelectAssignmentsView, self).get(request, *args, **kwargs)

    def get_queryset_for_role(self, role):
        queryset = super(PluginSelectAssignmentsView, self).get_queryset_for_role(role)
        queryset = queryset.filter(parentnode__id=role.id)
        return queryset

    def get_form_class(self):
        return PluginForm

    def get_initially_selected_queryset(self):
        """
        Select all assignments that must be approved by default.
        The user can then deselect desired assignments.

        Returns:
            QuerySet: Assignments for the role.
        """
        return self.get_queryset_for_role(self.request.cradmin_role)

    def form_valid(self, form):
        # Collect qualifying Assignment IDs
        qualifying_assignmentids = [item.id for item in form.cleaned_data['selected_items']]

        # Init results-collector and get the IDs of the RelatedStudents that qualify for exam.
        collector = resultscollector.PeriodResultSetCollector(period=self.request.cradmin_role,
                                                              qualifying_assignment_ids=qualifying_assignmentids)
        passing_relatedstudentids = collector.get_relatedstudents_that_qualify_for_exam()

        # Attach collected data to session.
        self.request.session['qualifying_assignmentids'] = qualifying_assignmentids
        self.request.session['passing_relatedstudentids'] = passing_relatedstudentids
        self.request.session['plugintypeid'] = PluginSelectAssignmentsView.plugintypeid
        return HttpResponseRedirect(self.request.cradmin_app.reverse_appurl('preview'))
