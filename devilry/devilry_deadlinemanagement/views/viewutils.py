# -*- coding: utf-8 -*-


from django.db import models
from django.views.generic import View
from django import http

from devilry.apps.core import models as core_models
from devilry.utils import datetimeutils


class DeadlineManagementMixin(View):
    """
    Manage deadline mixin that handles the fetching of valid querysets based on the handle_deadline_type and has
    general helper functions as utilities to streamline the implementation of subclasses.

    Note:
        All classes that implement this mixin requires that the ``CrAdminInstance`` used
        has an ``assignment`` property.
    """

    #: How are the deadlines to be handled?
    #: If a new attempt should be given, this will be:
    #: ``new-attempt``
    #: If the deadline should be moved, this will be:
    #: ``move-deadline``
    handle_deadline_type = None

    #: The current deadline fetched from kwargs
    #: in dispatch.
    deadline = None

    #: The :class:`~.devilry.apps.core.models.Assignment` we are
    #: managing deadlines for.
    assignment = None

    def dispatch(self, request, *args, **kwargs):
        self.assignment = self.request.cradmin_instance.assignment
        if 'deadline' in kwargs:
            self.deadline = datetimeutils.datetime_url_string_to_datetime(kwargs.get('deadline'))
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

    def get_backlink_url(self):
        """
        Override this function to provide a URL back to the app this
        view was accessed from.

        Note:
            By default this just redirects to back to the ``devilry_deadlinemanagement`` apps index view.
        """
        return self.request.cradmin_app.reverse_appindexurl()

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

    def __get_queryset_for_role_filtered_move_deadline(self, role):
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
        return queryset.filter(annotated_is_corrected=0)\
            .filter(cached_data__last_feedbackset__deadline_datetime=self.deadline)

    def __get_queryset_for_role_filtered_new_attempt(self, role):
        """
        Get the queryset of ``AssignmentGroups`` that should receive a new attempt.
        This excludes all groups where the last ``FeedbackSet`` is not corrected.

        Args:
            role: CrAdmin role.

        Returns:
            (QuerySet): of :obj:`~.devilry.apps.core.models.AssignmentGroup`s.
        """
        queryset = self.get_queryset_for_role_filtered(role=role)
        queryset = self.get_annotations_for_queryset(queryset=queryset)
        return queryset.filter(annotated_is_corrected__gt=0)\
            .filter(cached_data__last_feedbackset__deadline_datetime=self.deadline)

    def get_queryset_for_role_on_handle_deadline_type(self, role):
        """
        Returns the available groups based on the :attr:`.handle_deadline_type`.

        Args:
            role (:obj:`~.devilry.apps.core.models.Assigment`): CrAdmin role.

        Returns:
            (QuerySet): of :obj:`~.devilry.apps.core.models.AssignmentGroup`s.
        """
        if self.post_new_attempt:
            return self.__get_queryset_for_role_filtered_new_attempt(role=role)
        if self.post_move_deadline:
            return self.__get_queryset_for_role_filtered_move_deadline(role=role)
        raise http.Http404()

    def get_excluded_groups_count(self):
        """
        Get the number of excluded groups when handle_deadline_type was chosen.

        Returns:
            (int): number of ``AssignmentGroup``s excluded.
        """
        if not self.handle_deadline_type:
            return 0
        base_queryset = self.get_queryset_for_role_filtered(role=self.assignment)\
            .filter(cached_data__last_feedbackset__deadline_datetime=self.deadline)
        handle_deadline_based_queryset = self.get_queryset_for_role_on_handle_deadline_type(role=self.assignment)
        excluded_queryset = base_queryset\
            .exclude(id__in=handle_deadline_based_queryset.values_list('id', flat=True))
        return excluded_queryset.count()

    def get_excluded_groups_template(self):
        """
        Get the correct template base on :attr:`.handle_deadline_type`.

        Returns:
            (str): template path.
        """
        if self.post_new_attempt:
            return 'devilry_deadlinemanagement/includes/info-box-excluded-groups-new-attempt.django.html'
        if self.post_move_deadline:
            return 'devilry_deadlinemanagement/includes/info-box-excluded-groups-move-deadline.django.html'
        return 'devilry_deadlinemanagement/includes/info-box-base.django.html'

    def get_context_data(self, **kwargs):
        context_data = super(DeadlineManagementMixin, self).get_context_data(**kwargs)
        context_data['backlink_url'] = self.get_backlink_url()
        context_data['pagetitle'] = self.get_pagetitle()
        context_data['pageheading'] = self.get_pageheading()
        context_data['page_subheading'] = self.get_page_subheading()
        context_data['num_excluded_groups'] = self.get_excluded_groups_count()
        context_data['excluded_groups_info_box_template'] = self.get_excluded_groups_template()
        return context_data

    def form_valid_extra_check(self, form):
        """
        Override this in subclasses if extra an extra check is needed before posting.
        """
        return True
