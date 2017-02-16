# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django import http
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy
from django import forms
from django_cradmin.crispylayouts import DefaultSubmitBlock
from django_cradmin.crispylayouts import PrimarySubmitBlock

from django_cradmin.widgets.datetimepicker import DateTimePickerWidget
from django_cradmin.acemarkdown.widgets import AceMarkdownWidget
from django_cradmin.viewhelpers import formbase
from crispy_forms import layout

from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter
from devilry.devilry_deadlinemanagement.views import viewutils
from devilry.devilry_group import models as group_models
from devilry.utils import datetimeutils
from devilry.apps.core import models as core_models


class ManageDeadlinePostActionException(Exception):
    """
    """


class SelectedItemsForm(forms.Form):
    selected_items = forms.ModelMultipleChoiceField(
        queryset=core_models.AssignmentGroup.objects.none(),
        widget=forms.MultipleHiddenInput)

    def __init__(self, accessible_groups_queryset, *args, **kwargs):
        super(SelectedItemsForm, self).__init__(*args, **kwargs)
        self.fields['selected_items'].queryset = accessible_groups_queryset


class ManageDeadlineForm(SelectedItemsForm):
    comment_text = forms.CharField(
        widget=AceMarkdownWidget,
        help_text='Add a suitable comment or leave the default',
        initial=ugettext_lazy('You have been given a new attempt.')
    )

    new_deadline = forms.DateTimeField(
        widget=DateTimePickerWidget,
        help_text='Select a deadline'
    )

    def clean(self):
        super(ManageDeadlineForm, self).clean()
        if 'new_deadline' not in self.cleaned_data:
            raise forms.ValidationError('You must provide a deadline.')
        new_deadline = self.cleaned_data['new_deadline']
        if new_deadline <= timezone.now():
            raise forms.ValidationError('The deadline has to be in the future.')


class ManageDeadlineView(formbase.FormView):
    form_class = ManageDeadlineForm

    #: Move deadline button name as it will appear in request.POST
    move_deadline_button_name = 'move_deadline'

    #: New attempt button name as it will appear in request.POST
    new_attempt_button_name = 'new_attempt'

    #: Posted data from previous view as it will appear in request.POST
    post_type_received_data = 'post_type_received_data'

    def dispatch(self, request, *args, **kwargs):
        self.current_deadline = datetimeutils.string_to_datetime(kwargs.get('deadline'))
        return super(ManageDeadlineView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(ManageDeadlineView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.post_from_previous_view:
            if self.initial_selected_form_is_valid():
                return self.render_to_response(self.get_context_data(form=self.get_form()))
            else:
                return redirect(self.get_previous_view_url())
        else:
            return super(ManageDeadlineView, self).post(request, *args, **kwargs)

    @property
    def post_from_previous_view(self):
        return self.post_type_received_data in self.request.POST

    @property
    def post_move_deadline(self):
        return self.move_deadline_button_name in self.request.POST

    @property
    def post_new_attempt(self):
        return self.new_attempt_button_name in self.request.POST

    def initial_selected_form_is_valid(self):
        """
        Validate data posted from previous view.
        Returns:
            (bool): ``True`` if valid, else ``False``.
        """
        selected_form = SelectedItemsForm(
            accessible_groups_queryset=self.request.cradmin_app.get_accessible_group_queryset(),
            data=self.request.POST)
        return selected_form.is_valid()

    def get_form(self):
        """
        Instantiate the form with the correct inital values base on the type of input.

        If this view receives data in post from another view, we set the initial values for the form
        as the values that passed from the previous view.

        If not, the form is handles normally by Django.

        Returns:
            (:obj:`.ManageDeadlineForm`): instance.
        """
        if self.post_from_previous_view:
            form_class = self.get_form_class()
            return form_class(
                accessible_groups_queryset=self.request.cradmin_app.get_accessible_group_queryset(),
                initial={'selected_items': self.request.POST.getlist('selected_items')}
            )
        return super(ManageDeadlineView, self).get_form()

    def get_form_kwargs(self):
        kwargs = super(ManageDeadlineView, self).get_form_kwargs()
        kwargs['accessible_groups_queryset'] = self.request.cradmin_app.get_accessible_group_queryset()
        return kwargs

    def get_previous_view_url(self):
        return self.request.POST.get('previous_view_url', '/')

    def get_field_layout(self):
        return [
            layout.Div(
                'comment_text',
                'new_deadline',
                'selected_items',
                css_class='cradmin-globalfields')
        ]

    def get_buttons(self):
        return [
            PrimarySubmitBlock(self.move_deadline_button_name, self.get_submit_move_deadline_text()),
            DefaultSubmitBlock(self.new_attempt_button_name, self.get_submit_new_attempt_text())
        ]

    def get_submit_move_deadline_text(self):
        return 'Move current deadline'

    def get_submit_new_attempt_text(self):
        return 'Give new attempt'

    def __create_groupcomment(self, feedback_set_id, publishing_time, text):
        """
        Creates a new :class:`~.devilry.devilry_group.models.GroupComment` entry for a given ``FeedbackSet``.

        Args:
            feedback_set_id: ``GroupComment`` for.
            publishing_time: when the comment is published(visible).
            text: comment text.

        Returns:
            (int): ID of the created ``GroupComment``.
        """
        group_comment = group_models.GroupComment.objects.create(
            feedback_set_id=feedback_set_id,
            visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
            user=self.request.user,
            user_role=group_models.GroupComment.USER_ROLE_EXAMINER,
            text=text,
            comment_type=group_models.GroupComment.COMMENT_TYPE_GROUPCOMMENT,
            published_datetime=publishing_time
        )
        return group_comment.id

    def __create_feedbackset(self, group_id, deadline, created_datetime):
        """
        Creates a :class:`~.devilry.devilry_group.models.FeedbackSet` entry for a given ``AssignmentGroup``.

        Args:
            group_id: ``FeedbackSet`` for.
            deadline: the new deadline.
            created_datetime: when the FeedbackSet was created.

        Returns:
            (int): ID of the created ``FeedbackSet``.
        """
        feedbackset = group_models.FeedbackSet.objects.create(
            group_id=group_id,
            deadline_datetime=deadline,
            created_by=self.request.user,
            created_datetime=created_datetime
        )
        return feedbackset.id

    def __get_last_feedbackset_ids_from_posted_group_ids(self, form):
        """
        Get IDs of the last ``FeedbackSet``s on the groups that was posted.
        Args:
            form: form with group data.

        Returns:
            (list): of the posted groups last ``FeedbackSet`` IDs.
        """
        group_ids = self.__get_selected_group_ids(form=form)
        feedback_set_ids = core_models.AssignmentGroup.objects\
            .filter(id__in=group_ids)\
            .values_list('cached_data__last_feedbackset_id', flat=True)
        return list(feedback_set_ids)

    def __get_selected_group_ids(self, form):
        return [group.id for group in form.cleaned_data['selected_items']]

    def __move_deadline(self, deadline, text, form):
        """
        Moves the deadline of the last ``FeedbackSet`` for the selected ``AssignmentGroups``.

        Args:
            deadline: The new deadline.
            text: comment text.
            form: posted form.
        """
        feedback_set_ids = self.__get_last_feedbackset_ids_from_posted_group_ids(form)
        now_without_sec_and_micro = timezone.now().replace(second=0, microsecond=0)
        with transaction.atomic():
            devilryrole_type = self.request.devilryrole_type
            assignment = self.request.cradmin_role
            if self.current_deadline == assignment.first_deadline and devilryrole_type == 'admin':
                assignment = core_models.Assignment.objects.get(id=assignment.id)
                assignment.first_deadline = deadline
                assignment.full_clean()
                assignment.save()
            else:
                group_models.FeedbackSet.objects\
                    .filter(id__in=feedback_set_ids)\
                    .update(
                        deadline_datetime=deadline)
            for feedback_set_id in feedback_set_ids:
                self.__create_groupcomment(
                    feedback_set_id=feedback_set_id,
                    publishing_time=now_without_sec_and_micro,
                    text=text
                )

    def __give_new_attempt(self, deadline, text, assignment_group_ids):
        """
        Give a new attempt to the selected ``AssignmentGroups``. This will create new ``FeedbackSet``s with
        the new deadline, and an attached ``GroupComment``.

        Args:
            deadline: The new deadline.
            text: comment text.
            assignment_group_ids: groups that gets a new attempt.
        """
        now_without_sec_and_micro = timezone.now().replace(second=0, microsecond=0)
        with transaction.atomic():
            for group_id in assignment_group_ids:
                feedbackset_id = self.__create_feedbackset(
                    group_id=group_id,
                    deadline=deadline,
                    created_datetime=now_without_sec_and_micro
                )
                self.__create_groupcomment(
                    feedback_set_id=feedbackset_id,
                    publishing_time=now_without_sec_and_micro + timezone.timedelta(microseconds=1),
                    text=text
                )

    def form_valid(self, form):
        new_deadline = form.cleaned_data.get('new_deadline')
        comment_text = form.cleaned_data.get('comment_text')
        if self.post_move_deadline:
            self.__move_deadline(
                deadline=new_deadline,
                text=comment_text,
                form=form
            )
        elif self.post_new_attempt:
            self.__give_new_attempt(
                deadline=new_deadline,
                text=comment_text,
                assignment_group_ids=self.__get_selected_group_ids(form=form)
            )
        return super(ManageDeadlineView, self).form_valid(form)

    def form_invalid(self, form):
        print 'form invalid'
        return super(ManageDeadlineView, self).form_invalid(form)