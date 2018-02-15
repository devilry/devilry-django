from __future__ import unicode_literals

from django import forms
from django.contrib import messages
from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy

from devilry.devilry_cradmin import devilry_acemarkdown
from devilry.devilry_admin.views.assignment.students import groupview_base
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_group.models import FeedbacksetPassedPreviousPeriod


class TargetRenderer(devilry_listbuilder.assignmentgroup.GroupTargetRenderer):
    def get_submit_button_text(self):
        return ugettext_lazy('Pass students')

    def get_with_items_title(self):
        return ugettext_lazy('Students to pass')

    def get_field_layout(self):
        return [
            'feedback_comment_text'
        ]


class SelectedAssignmentGroupsForm(groupview_base.SelectedGroupsForm):
    """
    We subclass the :class:`~.devilry.devilry_admin.view.assignment.students.groupview_base.SelectedGroupsForm` form so
    that we can add a text widget for feedback comment.
    """
    def __init__(self, *args, **kwargs):
        super(SelectedAssignmentGroupsForm, self).__init__(*args, **kwargs)
        self.fields['feedback_comment_text'] = forms.CharField(
            widget=devilry_acemarkdown.Small,
            help_text=ugettext_lazy('Add a general comment to the feedback'),
            initial=ugettext_lazy('Delivery has been corrected. Passed in a previous semester.'),
            label=ugettext_lazy('Feedback comment text')
        )


class PassAssignmentGroupsView(groupview_base.BaseMultiselectView):
    """
    This workflow mitigates the problem of having no previous semesters that match the assignment on the current
    period, or if this for instance is a new subject derived from an old subject.

    This is basically the same as bulk correcting ``AssignmentGroups``, but can be done at an early stage from the
    admin dashboard.
    """
    template_name = 'devilry_admin/assignment/passed_previous_period/select_groups_to_pass.django.html'
    
    def get(self, request, *args, **kwargs):
        response = super(PassAssignmentGroupsView, self).get(request, *args, **kwargs)
        if self.get_unfiltered_queryset_for_role(role=self.request.cradmin_role).exists():
            return response
        else:
            messages.info(self.request,
                          ugettext_lazy('There are no students on this assignment.'))
            return redirect(self.get_success_url())

    def get_pagetitle(self):
        return ugettext_lazy('Bulk pass students')

    def get_form_class(self):
        return SelectedAssignmentGroupsForm

    def get_target_renderer_class(self):
        return TargetRenderer

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            viewname='manually_select_groups',
            kwargs={'filters_string': filters_string})

    def get_success_url(self):
        return self.request.cradmin_instance.rolefrontpage_url()

    def __get_grading_points(self):
        return self.assignment.max_points

    def __publish_grading_on_current_assignment(self, queryset, published_by):
        """
        Publish grading on current assignment ``self.assignment``

        Args:
            queryset: An :class:`~.devilry.apps.core.models.assignment_group.AssignmentGroup` ``QuerySet``.
            published_by: will be published by this user
        """
        grading_points = self.__get_grading_points()
        with transaction.atomic():
            for group in queryset:
                group.cached_data.last_feedbackset.publish(published_by, grading_points)
                FeedbacksetPassedPreviousPeriod(
                    feedbackset=group.cached_data.last_feedbackset,
                    passed_previous_period_type=FeedbacksetPassedPreviousPeriod.PASSED_PREVIOUS_SEMESTER_TYPES.MANUAL.value,
                    created_by=self.request.user
                ).save()

    def form_valid(self, form):
        queryset = form.cleaned_data['selected_items']
        self.__publish_grading_on_current_assignment(
            queryset=queryset,
            published_by=self.request.user)
        return redirect(self.get_success_url())
