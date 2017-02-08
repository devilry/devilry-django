# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django import http
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy
from django_cradmin.widgets.datetimepicker import DateTimePickerWidget

from devilry.apps.core import models as core_models
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_examiner.views.assignment.bulkoperations import bulk_operations_grouplist
from devilry.devilry_group.models import GroupComment, FeedbackSet


class NewAttemptDeadlineForm(bulk_operations_grouplist.SelectedAssignmentGroupForm):
    new_deadline = forms.DateTimeField(widget=DateTimePickerWidget)

    def clean(self):
        deadline = self.cleaned_data['new_deadline']
        if deadline <= timezone.now():
            raise forms.ValidationError('The deadline has to be in the future.')

    def get_new_deadline(self):
        return self.cleaned_data['new_deadline']


class NewAttemptDeadlineTargetRenderer(bulk_operations_grouplist.AssignmentGroupTargetRenderer):
    def get_field_layout(self):
        layout = super(NewAttemptDeadlineTargetRenderer, self).get_field_layout()
        layout.append('new_deadline')
        return layout


class BulkAddNewAttemptListView(bulk_operations_grouplist.AbstractAssignmentGroupItemListView):
    model = core_models.AssignmentGroup
    value_renderer_class = devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue
    template_name = 'devilry_examiner/assignment/bulk_new_attempt.django.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.cradmin_role.assignmentgroups.all().count() < 2:
            # Should not have access if assignment has less than 2 groups.
            raise http.Http404()
        return super(BulkAddNewAttemptListView, self).dispatch(request, *args, **kwargs)
    
    def get_pagetitle(self):
        return ugettext_lazy('Bulk add new attempt')

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'bulk-new-attempt-filter', kwargs={'filters_string': filters_string})

    def get_unfiltered_queryset_for_role(self, role):
        queryset = super(BulkAddNewAttemptListView, self).get_unfiltered_queryset_for_role(role)
        return queryset\
            .filter_examiner_has_access(user=self.request.user)\
            .filter(annotated_is_corrected=1)

    def get_target_renderer_class(self):
        return NewAttemptDeadlineTargetRenderer

    def get_form_class(self):
        return NewAttemptDeadlineForm

    def __create_groupcomment(self, feedback_set_id, publishing_time, text):
        GroupComment.objects.create(
            feedback_set_id=feedback_set_id,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
            user=self.request.user,
            user_role=GroupComment.USER_ROLE_EXAMINER,
            text=text,
            comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
            published_datetime=publishing_time
        )

    def __create_feedbackset(self, group_id, deadline_datetime, created_datetime):
        feedbackset = FeedbackSet.objects.create(
            group_id=group_id,
            deadline_datetime=deadline_datetime,
            created_by=self.request.user,
            created_datetime=created_datetime
        )
        return feedbackset.id

    def form_valid(self, form):
        group_ids = self.get_selected_groupids(posted_form=form)
        new_deadline = form.get_new_deadline()
        comment_text = form.cleaned_data['feedback_comment_text']
        anonymous_displaynames = self.get_group_anonymous_displaynames(form=form)

        now_without_sec_and_micro = timezone.now().replace(second=0, microsecond=0)
        with transaction.atomic():
            for group_id in group_ids:
                feedbackset_id = self.__create_feedbackset(
                    group_id=group_id,
                    deadline_datetime=new_deadline,
                    created_datetime=now_without_sec_and_micro)
                self.__create_groupcomment(
                    feedback_set_id=feedbackset_id,
                    publishing_time=now_without_sec_and_micro + timezone.timedelta(microseconds=1),
                    text=comment_text)
        self.add_success_message(anonymous_displaynames)
        return super(BulkAddNewAttemptListView, self).form_valid(form=form)
    
    def add_success_message(self, anonymous_display_names):
        message = ugettext_lazy('Bulk added new attempt for %(group_names)s') % {
            'group_names': ', '.join(anonymous_display_names)}
        messages.success(self.request, message=message)

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appindexurl()
