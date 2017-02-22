# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.views.generic import View
from django import http

from devilry.apps.core import models as core_models
from devilry.utils import datetimeutils


class DeadlineManagementMixin(View):
    #: How are the deadlines to be handled?
    #: If a new attempt should be given, this will be:
    #: ``new-attempt``
    #: If the deadline should be moved, this will be:
    #: ``move-deadline``
    handle_deadline_type = None

    #: The current deadline fetched from kwargs
    #: in dispatch.
    deadline = None

    def dispatch(self, request, *args, **kwargs):
        if 'deadline' in kwargs:
            self.deadline = datetimeutils.string_to_datetime(kwargs.get('deadline'))
        if 'handle_deadline' in kwargs:
            self.handle_deadline_type = kwargs.get('handle_deadline')
        return super(DeadlineManagementMixin, self).dispatch(request, *args, **kwargs)

    @property
    def post_move_deadline(self):
        return self.handle_deadline_type == 'move-deadline'

    @property
    def post_new_attempt(self):
        return self.handle_deadline_type == 'new-attempt'

    def get_pagetitle(self):
        return ''

    def get_pageheading(self):
        return ''

    def get_page_subheading(self):
        return ''

    def get_startapp_backlink_url(self):
        """
        Override this function to provide a URL back to the app this
        view was accessed from.

        Note:
            By default this just redirects to back to the apps index view.
        """
        return self.request.cradmin_app.reverse_appindexurl()

    def get_context_data(self, **kwargs):
        context_data = super(DeadlineManagementMixin, self).get_context_data(**kwargs)
        context_data['startapp_backlink_url'] = self.get_startapp_backlink_url()
        context_data['pagetitle'] = self.get_pagetitle()
        context_data['pageheading'] = self.get_pageheading()
        context_data['page_subheading'] = self.get_page_subheading()
        return context_data

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
            .annotate_with_is_corrected_count()\
            .annotate_with_is_passing_grade_count()

    def get_queryset_for_role_filtered(self, role):
        """
        Get a queryset of ``AssignmentGroup``s filtered by the role.
        Examiners, Candidates and cached data is joined.

        Args:
            role: CrAdmin role.

        Returns:
            (QuerySet): of :obj:`~.devilry.apps.core.models.AssignmentGroup`s.
        """
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

    def get_queryset_for_role_filtered_move_deadline(self, role):
        """
        Get the queryset of ``AssignmentGroups`` that should be moved.
        This excludes all groups where the last ``FeedbackSet`` has been corrected.

        Args:
            role: CrAdmin role.

        Returns:
            (QuerySet): of :obj:`~.devilry.apps.core.models.AssignmentGroup`s.
        """
        queryset = self.get_queryset_for_role_filtered(role=role)
        queryset = self.get_annotations_for_queryset(queryset=queryset)
        return queryset.filter(annotated_is_corrected=0)

    def get_queryset_for_role_filtered_new_attempt(self, role):
        """
        Get the queryset of ``AssignmentGroups`` that should receive a new attempt.
        This excludes all groups where the last ``FeedbackSet`` is not corrected..

        Args:
            role: CrAdmin role.

        Returns:
            (QuerySet): of :obj:`~.devilry.apps.core.models.AssignmentGroup`s.
        """
        queryset = self.get_queryset_for_role_filtered(role=role)
        queryset = self.get_annotations_for_queryset(queryset=queryset)
        return queryset.filter(annotated_is_corrected__gt=0)

    def get_queryset_for_role_on_handle_deadline_type(self, role):
        """
        Returns the available groups based on the :attr:`.handle_deadline_type`.
        Args:
            role (:obj:`~.devilry.apps.core.models.Assigment`): CrAdmin role.

        Returns:

        """
        if self.post_new_attempt:
            return self.get_queryset_for_role_filtered_new_attempt(role=role)\
                .filter(cached_data__last_feedbackset__deadline_datetime=self.deadline)
        if self.post_move_deadline:
            return self.get_queryset_for_role_filtered_move_deadline(role=role)\
                .filter(cached_data__last_feedbackset__deadline_datetime=self.deadline)
        raise http.Http404()

    def selected_items_in_form_matches_handle_deadline_rules(self, form):
        """
        Checks that no unavailable groups have been added to the selected items.

        This is verified based on two simple rules:
            If the groups are to be given a new attempt, all the groups last feedbackset must be
            corrected.

            If the groups are to have their deadlines moved, all the groups last feedbackset must NOT have been
            corrected.

        If the number of feedbacksets from the queryset does NOT match the number of selected items
        in the form, this means that some of the feedbacksets have been changed by another user or
        groups that does not meet the requirements for the given deadline handling(new-attempt or move-deadline)
        have been injected in some way.

        Args:
            form: Django form.

        Raises:
            (Http404): if requirements are not met.
        """
        assignment = self.request.cradmin_role
        queryset = self.get_queryset_for_role_on_handle_deadline_type(role=assignment)
        if queryset.count() != form.cleaned_data['selected_items'].count():
            raise http.Http404()
