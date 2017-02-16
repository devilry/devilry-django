# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.db import models
from django import http
from django.utils.translation import ugettext_lazy
from django_cradmin.acemarkdown.widgets import AceMarkdownWidget
from django_cradmin.viewhelpers import multiselect2
from django_cradmin.viewhelpers import multiselect2view
from django_cradmin.crispylayouts import PrimarySubmitBlock, DefaultSubmitBlock

from devilry.apps.core import models as core_models
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter
from devilry.utils import datetimeutils


class GroupQuerySetMixin(object):

    def get_candidate_queryset(self):
        return core_models.Candidate.objects\
            .select_related('relatedstudent__user')\
            .only(
                'candidate_id',
                'assignment_group',
                'relatedstudent__candidate_id',
                'relatedstudent__automatic_anonymous_id',
                'relatedstudent__user__shortname',
                'relatedstudent__user__fullname',
            )

    def get_examiner_queryset(self):
        return core_models.Examiner.objects\
            .select_related('relatedexaminer__user')\
            .only(
                'relatedexaminer',
                'assignmentgroup',
                'relatedexaminer__automatic_anonymous_id',
                'relatedexaminer__user__shortname',
                'relatedexaminer__user__fullname',
            )

    def get_queryset_for_role_filtered(self, role):
        queryset = self.request.cradmin_app.get_accessible_group_queryset()
        assignment = role
        return queryset\
            .filter(parentnode=assignment)\
            .prefetch_related(
                models.Prefetch(
                    'candidates',
                    queryset=self.get_candidate_queryset()))\
            .prefetch_related(
                models.Prefetch(
                    'examiners',
                    queryset=self.get_examiner_queryset()))\
            .select_related(
                'cached_data__last_published_feedbackset',
                'cached_data__last_feedbackset',
                'cached_data__first_feedbackset',
                'parentnode'
            )


class SelectedAssignmentGroupForm(forms.Form):
    qualification_modelclass = core_models.AssignmentGroup
    invalid_qualification_item_message = 'Invalid assignment group items was selected.'

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
    descriptive_item_name = 'assignment group'

    def __init__(self, deadline, *args, **kwargs):
        super(AssignmentGroupTargetRenderer, self).__init__(*args, **kwargs)
        self.deadline = deadline

    def get_move_deadline_text(self):
        return 'Move deadline for selected {}(s)'.format(self.descriptive_item_name)

    def get_submit_button_text(self):
        return 'New attempt for selected {}(s)'.format(self.descriptive_item_name)

    def get_with_items_title(self):
        return 'Selected {}'.format(self.descriptive_item_name)

    def get_without_items_text(self):
        return 'No {} selected'.format(self.descriptive_item_name)


class AbstractAssignmentGroupMultiSelectListFilterView(GroupQuerySetMixin, multiselect2view.ListbuilderFilterView):
    """
    Abstract class that implements ``ListbuilderFilterView``.

    Adds anonymization and activity filters for the ``AssignmentGroup``s.
    Fetches the ``AssignmentGroups`` through :meth:`~.get_unfiltered_queryset_for_role` and joins
    necessary tables used for anonymzation and annotations used by viewfilters.
    """
    model = core_models.AssignmentGroup

    def dispatch(self, request, *args, **kwargs):
        num_filtered_groups = self.get_unfiltered_queryset_for_role(self.request.cradmin_role).count()
        if num_filtered_groups < 2:
            # Should not have access if assignment has less than two corrected groups.
            raise http.Http404()
        self.assignment = self.request.cradmin_role
        self.deadline = datetimeutils.string_to_datetime(kwargs.get('deadline'))
        return super(AbstractAssignmentGroupMultiSelectListFilterView, self).dispatch(request, *args, **kwargs)

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
        """
        Adds filters to use in the view.

        Override this to add more filters
        """
        if self.assignment.is_anonymous:
            self.__add_anonymization_filters_for_items(filterlist=filterlist)
        else:
            self.__add_filterlist_items_not_anonymous(filterlist=filterlist)
        filterlist.append(devilry_listfilter.assignmentgroup.ActivityFilter())

    def get_annotations_for_queryset(self, queryset):
        """
        Add annotations for the the queryset.
        This function is called in ``get_unfiltered_queryset_for_role()``

        Args:
            queryset (QuerySet): Add annotations to.

        Returns:
            (QuerySet): annotated queryset.
        """
        return queryset \
            .annotate_with_is_waiting_for_feedback_count() \
            .annotate_with_is_waiting_for_deliveries_count() \
            .annotate_with_is_corrected_count()

    def get_unfiltered_queryset_for_role(self, role):
        """
        Get unfiltered ``QuerySet`` of :obj:`~.devilry.apps.core.models.AssignmentGroup`s.

        Override this with a call to super and more filters to the queryset.

        Args:
            role (:class:`~.devilry.apps.core.models.Assignment`): cradmin role.

        Returns:
            (QuerySet): ``QuerySet`` of ``AssignmentGroups``.
        """
        queryset = self.get_queryset_for_role_filtered(role=role)
        queryset = self.get_annotations_for_queryset(queryset=queryset)
        return queryset \
            .filter(annotated_is_corrected__gt=0)\
            .filter(cached_data__last_published_feedbackset__deadline_datetime=self.deadline)

    def get_value_and_frame_renderer_kwargs(self):
        return {
            'assignment': self.assignment
        }

    def get_target_renderer_kwargs(self):
        kwargs = super(AbstractAssignmentGroupMultiSelectListFilterView, self).get_target_renderer_kwargs()
        kwargs['deadline'] = self.deadline
        return kwargs

    def get_form_kwargs(self):
        kwargs = super(AbstractAssignmentGroupMultiSelectListFilterView, self).get_form_kwargs()
        kwargs['selectable_items_queryset'] = self.get_unfiltered_queryset_for_role(self.request.cradmin_role)
        kwargs['assignment'] = self.request.cradmin_role
        return kwargs

    def get_selected_groupids(self, posted_form):
        return [item.id for item in posted_form.cleaned_data['selected_items']]

    def get_feedbackset_ids_from_posted_ids(self, form):
        """
        Get list of ids of the last :class:`~.devilry.devilry_group.models.FeedbackSet` from each ``AssignmentGroup``
        in ``form``s cleaned data.

        Args:
            form: cleaned form.

        Returns:
            (list): list of ``FeedbackSet`` ids.
        """
        group_ids = self.get_selected_groupids(posted_form=form)
        feedback_set_ids = self.get_unfiltered_queryset_for_role(role=self.request.cradmin_role) \
            .filter(id__in=group_ids) \
            .values_list('cached_data__last_feedbackset_id', flat=True)
        return list(feedback_set_ids)

    def get_group_anonymous_displaynames(self, form):
        """
        Build a list of anonymized displaynames for the groups that where corrected.

        Args:
            form: posted form

        Returns:
            (list): list of anonymized displaynames for the groups
        """
        groups = form.cleaned_data['selected_items']
        anonymous_display_names = [unicode(group.get_anonymous_displayname(assignment=self.request.cradmin_role))
                                   for group in groups]
        return anonymous_display_names

    def get_success_url(self):
        """
        Defaults to the apps indexview.
        """
        return self.request.cradmin_app.reverse_appindexurl()

    def form_valid(self, form):
        return super(AbstractAssignmentGroupMultiSelectListFilterView, self).form_valid(form)

    def get_filterlist_url(self, filters_string):
        raise NotImplementedError()

    def add_success_message(self, anonymous_display_names):
        """
        Add list of anonymized displaynames of the groups that received feedback.

        Args:
            anonymous_display_names (list): List of anonymized displaynames for groups.
        """
        raise NotImplementedError()