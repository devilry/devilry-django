from __future__ import unicode_literals

from django import forms
from django.db import models
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext_lazy as _, ugettext_lazy, pgettext_lazy
from django.views.generic import View

from django_cradmin.viewhelpers import multiselect2
from django_cradmin.viewhelpers import multiselect2view
from django_cradmin.acemarkdown.widgets import AceMarkdownWidget

from devilry.devilry_cradmin import devilry_listbuilder
from devilry.apps.core import models as core_models
from devilry.devilry_dbcache.models import AssignmentGroupCachedData
from devilry.devilry_group import models as group_models
from devilry.devilry_comment import models as comment_models


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

    #: A wysiwig editor for writing a feedback message.
    feedback_comment_text = forms.CharField(widget=AceMarkdownWidget, help_text='Add a general comment to the feedback')

    def __init__(self, *args, **kwargs):
        selectable_qualification_items_queryset = kwargs.pop('selectable_items_queryset')
        self.assignment = kwargs.pop('assignment')
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
        return 'Submit selected {}(s)'.format(self.descriptive_item_name)

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
        label=pgettext_lazy('Points'))

    def get_grading_points(self):
        return self.cleaned_data['points']


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
            required=False)

    def get_grading_points(self):
        if self.cleaned_data['passed']:
            return self.assignment.max_points
        else:
            return 0


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
        cache_queryset = AssignmentGroupCachedData.objects\
            .filter(group__parentnode=role)\
            .exclude(models.Q(last_published_feedbackset=models.F('last_feedbackset')))\
            .values_list('group_id')
        group_queryset = self.model.objects\
            .filter(id__in=cache_queryset)\
            .filter_examiner_has_access(user=self.request.user)
        return group_queryset

    def get_form_kwargs(self):
        kwargs = super(AssignmentGroupItemListView, self).get_form_kwargs()
        kwargs['selectable_items_queryset'] = self.get_queryset_for_role(self.request.cradmin_role)
        kwargs['assignment'] = self.request.cradmin_role
        return kwargs

    def get_selected_groupids(self, posted_form):
        selected_group_ids = [item.id for item in posted_form.cleaned_data['selected_items']]
        return selected_group_ids

    def form_valid(self, form):
        group_ids = self.get_selected_groupids(posted_form=form)
        group_queryset = core_models.AssignmentGroup.objects.filter(id__in=group_ids)
        cached_data = AssignmentGroupCachedData.objects.filter(group__in=group_queryset)
        feedback_sets = [cache.last_feedbackset for cache in cached_data]
        points = form.get_grading_points()
        text = form.cleaned_data['feedback_comment_text']
        for feedback_set in feedback_sets:
            group_models.GroupComment.objects.create(
                feedback_set=feedback_set,
                part_of_grading=True,
                visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                user=self.request.user,
                user_role=comment_models.Comment.USER_ROLE_EXAMINER,
                text=text,
                comment_type=comment_models.Comment.COMMENT_TYPE_GROUPCOMMENT,
            )
            feedback_set.publish(published_by=self.request.user, grading_points=points)
        return super(AssignmentGroupItemListView, self).form_valid(form=form)

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appindexurl()


class BulkFeedbackPointsView(AssignmentGroupItemListView):
    """
    Handles bulkfeedback for assignment with points-based grading system.
    """
    def get_target_renderer_class(self):
        return PointsTargetRenderer

    def get_form_class(self):
        return AssignPointsForm


class BulkFeedbackPassedFailedView(AssignmentGroupItemListView):
    """
    Handles bulkfeedback for assignment with passed/failed grading system.
    """
    def get_target_renderer_class(self):
        return PassedFailedTargetRenderer

    def get_form_class(self):
        return AssignPassedFailedForm


class BulkFeedbackRedirectView(View):
    """
    Redirects to the appropriate view based on the assignments grading system type.
    """
    def dispatch(self, request, *args, **kwargs):
        grading_plugin_id = self.request.cradmin_role.grading_system_plugin_id
        if grading_plugin_id == core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS:
            return HttpResponseRedirect(request.cradmin_app.reverse_appurl('bulk-feedback-points'))
        grading_plugin_id = self.request.cradmin_role.grading_system_plugin_id
        if grading_plugin_id == core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED:
            return HttpResponseRedirect(request.cradmin_app.reverse_appurl('bulk-feedback-passedfailed'))
        return Http404()
