from __future__ import unicode_literals

from django import forms
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext_lazy as _, ugettext_lazy, pgettext_lazy
from django.views.generic import View

from django_cradmin.viewhelpers import multiselect2
from django_cradmin.viewhelpers import multiselect2view
from django_cradmin.acemarkdown.widgets import AceMarkdownWidget

from devilry.apps.core import models as core_models


class SelectedAssignmentGroupForm(forms.Form):
    qualification_modelclass = core_models.AssignmentGroup
    invalid_qualification_item_message = 'Invalid assingment group items was selected.'

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

    #: A wysiwig editor for writing a feedback message.
    feedback_comment_text = forms.CharField(widget=AceMarkdownWidget, help_text='Add a general comment to the feedback')

    def __init__(self, *args, **kwargs):
        selectable_qualification_items_queryset = kwargs.pop('selectable_items_queryset')
        super(SelectedAssignmentGroupForm, self).__init__(*args, **kwargs)
        self.fields['selected_items'].queryset = selectable_qualification_items_queryset


class SelectedAssignmentGroupItem(multiselect2.selected_item_renderer.SelectedItem):
    def get_title(self):
        return self.value


class SelectableAssignmentGroupItemValue(multiselect2.listbuilder_itemvalues.ItemValue):
    selected_item_renderer_class = SelectedAssignmentGroupItem

    def get_inputfield_name(self):
        return 'selected_items'

    def get_title(self):
        return self.value

    def get_description(self):
        return ''


class AssignmentGroupTargetRenderer(multiselect2.target_renderer.Target):

    #: The selected item as it is shown when selected.
    #: By default this is :class:`.SelectedQualificationItem`.
    selected_target_renderer = SelectedAssignmentGroupItem

    #: A descriptive name for the items selected.
    descriptive_item_name = 'assignment group'

    def get_submit_button_text(self):
        return 'Submit selected {}'.format(self.descriptive_item_name)

    def get_with_items_title(self):
        return 'Selected {}'.format(self.descriptive_item_name)

    def get_without_items_text(self):
        return 'No {} selected'.format(self.descriptive_item_name)

    def get_field_layout(self):
        return [
            'feedback_comment_text'
        ]


class AssignPointsForm(SelectedAssignmentGroupForm):
    points = forms.IntegerField(
        min_value=0,
        help_text='Add a score that will be given to all selected assignment groups.',
        required=True,
    )


class PointsTargetRenderer(AssignmentGroupTargetRenderer):
    def get_field_layout(self):
        layout = super(PointsTargetRenderer, self).get_field_layout()
        layout.append('points')
        return layout


class AssignPassedFailedForm(SelectedAssignmentGroupForm):
    #: Set delivery as passed or failed.
    passed = forms.BooleanField(
            label=pgettext_lazy('grading', 'Passed?'),
            help_text=pgettext_lazy('grading', 'Check to provide a passing grade.'),
            initial=True,
            required=True)


class PassedFailedTargetRenderer(AssignmentGroupTargetRenderer):
    def get_field_layout(self):
        layout = super(PassedFailedTargetRenderer, self).get_field_layout()
        layout.append('passed')
        return layout


class AssignmentGroupItemListView(multiselect2view.ListbuilderView):
    """

    """
    class Meta:
        abstract = True

    #: The model represented as a selectable item.
    model = core_models.AssignmentGroup
    value_renderer_class = SelectableAssignmentGroupItemValue

    def get_default_paginate_by(self, queryset):
        return 10

    def get_queryset_for_role(self, role):
        queryset = self.model.objects.all()
        return queryset.filter(parentnode__id=role.id)

    def get_form_kwargs(self):
        kwargs = super(AssignmentGroupItemListView, self).get_form_kwargs()
        kwargs['selectable_items_queryset'] = self.get_queryset_for_role(self.request.cradmin_role)
        return kwargs

    def get_selected_groupids(self, posted_form):
        return [item.id for item in posted_form.cleaned_data['selected_items']]

    def form_valid(self, form):
        return None


class BulkFeedbackPointsView(AssignmentGroupItemListView):
    """
    Handles bulkfeedback for assignment with points-based grading system.
    """
    def get_target_renderer_class(self):
        return PointsTargetRenderer

    def get_form_class(self):
        return AssignPointsForm

    def form_valid(self, form):
        groupids = self.get_selected_groupids(posted_form=form)
        return None


class BulkFeedbackPassedFailedView(AssignmentGroupItemListView):
    """
    Handles bulkfeedback for assignment with passed/failed grading system.
    """
    def get_target_renderer_class(self):
        return PassedFailedTargetRenderer

    def get_form_class(self):
        return AssignPassedFailedForm

    def form_valid(self, form):
        group_ids = self.get_selected_groupids(posted_form=form)
        return None


class BulkFeedbackView(View):
    """
    Redirects to the appropriate view based on the assignments grading system type.
    """
    def dispatch(self, request, *args, **kwargs):
        grading_plugin_id = self.request.cradmin_role.grading_system_plugin_id
        if grading_plugin_id == core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS:
            print 'redirecting to points view'
            return HttpResponseRedirect(request.cradmin_app.reverse_appurl('bulk-feedback-points'))
        grading_plugin_id = self.request.cradmin_role.grading_system_plugin_id
        if grading_plugin_id == core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED:
            print 'redirecting to passed/failed view'
            return HttpResponseRedirect(request.cradmin_app.reverse_appurl('bulk-feedback-passedfailed'))
        return Http404()
