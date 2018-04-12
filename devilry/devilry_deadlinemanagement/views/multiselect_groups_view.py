# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from crispy_forms import layout
from django import forms
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy
from django_cradmin.viewhelpers import multiselect2
from django_cradmin.viewhelpers import multiselect2view

from devilry.apps.core import models as core_models
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter
from devilry.utils import datetimeutils
from devilry.devilry_deadlinemanagement.views import viewutils


class SelectedAssignmentGroupForm(forms.Form):
    qualification_modelclass = core_models.AssignmentGroup
    invalid_qualification_item_message = ugettext_lazy(
        'Something went wrong. This may happen if someone else performed a similar operation '
        'while you where selecting. Refresh the page and try again')

    #: The items selected as ModelMultipleChoiceField.
    #: If some or all items should be selected by default, override this.
    selected_items = forms.ModelMultipleChoiceField(

        # No items are selectable by default.
        queryset=None,

        # Used if the object to select for some reason does
        # not exist(has been deleted or altered in some way)
        error_messages={
            'invalid_choice': invalid_qualification_item_message,
        }
    )

    def __init__(self, *args, **kwargs):
        selectable_qualification_items_queryset = kwargs.pop('selectable_items_queryset')
        self.assignment = kwargs.pop('assignment')
        super(SelectedAssignmentGroupForm, self).__init__(*args, **kwargs)
        self.fields['selected_items'].queryset = selectable_qualification_items_queryset


class AssignmentGroupTargetRenderer(multiselect2.target_renderer.Target):

    #: The selected item as it is shown when selected.
    #: By default this is :class:`.SelectedQualificationItem`.
    selected_target_renderer = devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue

    #: A descriptive name for the items selected.
    descriptive_item_name = ugettext_lazy('groups')

    def get_move_deadline_text(self):
        return pgettext_lazy(
            'assignment_group_target_renderer move_dealine_text',
            'Move deadline for selected %(what)s'
        ) % {'what': self.descriptive_item_name}

    def get_submit_button_text(self):
        return pgettext_lazy(
            'assignment_group_target_renderer submit_button_text',
            'Continue with selected %(what)s'
        ) % {'what': self.descriptive_item_name}

    def get_with_items_title(self):
        return pgettext_lazy(
            'assignment_group_target_renderer with_items_title',
            'Selected %(what)s'
        ) % {'what': self.descriptive_item_name}

    def get_without_items_text(self):
        return pgettext_lazy(
            'assignment_group_target_renderer without_items_text',
            'No %(what)s selected'
        ) % {'what': self.descriptive_item_name}

    def get_hidden_fields(self):
        return [
            layout.Hidden(name='post_type_received_data', value='')
        ]


class AssignmentGroupMultiSelectListFilterView(viewutils.DeadlineManagementMixin, multiselect2view.ListbuilderFilterView):
    """
    Abstract class that implements ``ListbuilderFilterView``.

    Adds anonymization and activity filters for the ``AssignmentGroup``s.
    Fetches the ``AssignmentGroups`` through :meth:`~.get_unfiltered_queryset_for_role` and joins
    necessary tables used for anonymzation and annotations used by viewfilters.
    """
    model = core_models.AssignmentGroup
    value_renderer_class = devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue
    template_name = 'devilry_deadlinemanagement/deadline-bulk-multiselect-filterlistview.django.html'
    handle_deadline_type = None

    def get_pagetitle(self):
        return pgettext_lazy('assignment_group_multiselect_list_filter_view pagetitle',
                             'Select groups')

    def get_pageheading(self):
        return pgettext_lazy('assignment_group_multiselect_list_filter_view pageheading',
                             'Select groups')

    def get_page_subheading(self):
        return pgettext_lazy('assignment_group_multiselect_list_filter_view page_subheading',
                             'Select the groups you want to manage the deadline for.')

    def get_default_paginate_by(self, queryset):
        return 5

    def __add_filterlist_items_anonymous_uses_custom_candidate_ids(self, filterlist):
        filterlist.append(devilry_listfilter.assignmentgroup.SearchAnonymousUsesCustomCandidateIds())
        filterlist.append(devilry_listfilter.assignmentgroup.OrderByAnonymousUsesCustomCandidateIds())

    def __add_filterlist_items_anonymous(self, filterlist):
        filterlist.append(devilry_listfilter.assignmentgroup.SearchAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.OrderByAnonymous(include_points=False))

    def __add_filterlist_items_not_anonymous(self, filterlist):
        filterlist.append(devilry_listfilter.assignmentgroup.SearchNotAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.OrderByNotAnonymous(include_points=False))

    def __add_anonymization_filters_for_items(self, filterlist):
        """
        Adds filters based on the :attr:`~.devilry.apps.core.models.anonymizationmode` of the
        ``Assignment``.
        """
        if self.assignment.uses_custom_candidate_ids:
            self.__add_filterlist_items_anonymous_uses_custom_candidate_ids(filterlist=filterlist)
        else:
            self.__add_filterlist_items_anonymous(filterlist=filterlist)

    def add_filterlist_items(self, filterlist):
        super(AssignmentGroupMultiSelectListFilterView, self).add_filterlist_items(filterlist)
        if self.assignment.is_anonymous:
            self.__add_anonymization_filters_for_items(filterlist=filterlist)
        else:
            self.__add_filterlist_items_not_anonymous(filterlist=filterlist)
        filterlist.append(devilry_listfilter.assignmentgroup.ActivityFilter())
        filterlist.append(devilry_listfilter.assignmentgroup.IsPassingGradeFilter())
        filterlist.append(devilry_listfilter.assignmentgroup.PointsFilter())

    def get_unfiltered_queryset_for_role(self, role):
        return self.get_queryset_for_role_on_handle_deadline_type(role=role)

    def get_target_renderer_class(self):
        return AssignmentGroupTargetRenderer

    def get_form_class(self):
        return SelectedAssignmentGroupForm

    def get_value_and_frame_renderer_kwargs(self):
        return {
            'assignment': self.assignment
        }

    def get_form_kwargs(self):
        kwargs = super(AssignmentGroupMultiSelectListFilterView, self).get_form_kwargs()
        kwargs['selectable_items_queryset'] = self.get_unfiltered_queryset_for_role(self.assignment)
        kwargs['assignment'] = self.assignment
        return kwargs

    def get_target_renderer_kwargs(self):
        kwargs = super(AssignmentGroupMultiSelectListFilterView, self).get_target_renderer_kwargs()
        kwargs['form_action'] = self.request.cradmin_app.reverse_appurl(
            viewname='manage-deadline-post',
            kwargs={
                'deadline': datetimeutils.datetime_to_url_string(self.deadline),
                'handle_deadline': self.handle_deadline_type
            })
        return kwargs

    def get_selected_groupids(self, posted_form):
        return [item.id for item in posted_form.cleaned_data['selected_items']]

    def get_group_anonymous_displaynames(self, form):
        """
        Build a list of anonymized displaynames for the groups that where corrected.

        Args:
            form: posted form

        Returns:
            (list): list of anonymized displaynames for the groups
        """
        groups = form.cleaned_data['selected_items']
        anonymous_display_names = [
            unicode(group.get_anonymous_displayname(assignment=self.assignment))
            for group in groups]
        return anonymous_display_names

    def get_success_url(self):
        """
        Defaults to the apps indexview.
        """
        return self.request.cradmin_app.reverse_appindexurl()

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'select-groups-manually-filter', kwargs={
                'deadline': datetimeutils.datetime_to_url_string(self.deadline),
                'handle_deadline': self.handle_deadline_type,
                'filters_string': filters_string
            })
