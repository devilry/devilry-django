# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django import http
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy
from django_cradmin.widgets.datetimepicker import DateTimePickerWidget

from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter
from devilry.devilry_deadlinemanagement.views import viewutils
from devilry.devilry_group import models as group_models
from devilry.utils import datetimeutils


class NewAttemptDeadlineForm(viewutils.SelectedAssignmentGroupForm):
    new_deadline = forms.DateTimeField(widget=DateTimePickerWidget)
    invalid_qualification_item_message = pgettext_lazy(
        'examiner group multiselect submit',
        'Something went wrong. This may happen if someone else performed a similar operation '
        'while you where selecting. Refresh the page and try again')

    def clean(self):
        if 'new_deadline' not in self.cleaned_data:
            raise forms.ValidationError('You must provide a deadline.')
        deadline = self.cleaned_data['new_deadline']
        if deadline <= timezone.now():
            raise forms.ValidationError('The deadline has to be in the future.')

    def get_new_deadline(self):
        return self.cleaned_data['new_deadline']


class NewAttemptDeadlineTargetRenderer(viewutils.AssignmentGroupTargetRenderer):
    def get_field_layout(self):
        layout = super(NewAttemptDeadlineTargetRenderer, self).get_field_layout()
        layout.append('new_deadline')
        return layout


class BulkManageDeadlineMultiSelectView(viewutils.AbstractAssignmentGroupMultiSelectListFilterView):
    value_renderer_class = devilry_listbuilder.assignmentgroup.ExaminerMultiselectItemValue
    template_name = 'devilry_deadlinemanagement/deadline-bulk-multiselect-filterlistview.django.html'

    def dispatch(self, request, *args, **kwargs):
        self.deadline = datetimeutils.string_to_datetime(kwargs.get('deadline'))
        return super(BulkManageDeadlineMultiSelectView, self).dispatch(request, *args, **kwargs)

    def get_pagetitle(self):
        return ugettext_lazy('Manage groups on deadline')

    def add_filterlist_items(self, filterlist):
        super(BulkManageDeadlineMultiSelectView, self).add_filterlist_items(filterlist)
        filterlist.append(devilry_listfilter.assignmentgroup.IsPassingGradeFilter())
        filterlist.append(devilry_listfilter.assignmentgroup.PointsFilter())

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'choose-manually-filter', kwargs={
                'deadline': datetimeutils.datetime_to_string(self.deadline),
                'filters_string': filters_string
            })

    def get_target_renderer_class(self):
        return NewAttemptDeadlineTargetRenderer

    def get_form_class(self):
        return NewAttemptDeadlineForm

    def __create_groupcomment(self, feedback_set_id, publishing_time, text):
        group_models.GroupComment.objects.create(
            feedback_set_id=feedback_set_id,
            visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
            user=self.request.user,
            user_role=group_models.GroupComment.USER_ROLE_EXAMINER,
            text=text,
            comment_type=group_models.GroupComment.COMMENT_TYPE_GROUPCOMMENT,
            published_datetime=publishing_time
        )

    def __create_feedbackset(self, group_id, deadline_datetime, created_datetime):
        feedbackset = group_models.FeedbackSet.objects.create(
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

        if 'move_deadline' in self.request.POST:
            print 'MOVE DEADLINE'
        elif 'new_attempt' in self.request.POST:
            print 'NEW ATTEMPT'

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
        return super(BulkManageDeadlineMultiSelectView, self).form_valid(form=form)

    def add_success_message(self, anonymous_display_names):
        message = ugettext_lazy('Bulk added new attempt for %(group_names)s') % {
            'group_names': ', '.join(anonymous_display_names)}
        messages.success(self.request, message=message)

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appindexurl()
