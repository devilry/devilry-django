import math

from django.core.exceptions import ValidationError
from django.db import models, transaction

from devilry.apps.core.models import Assignment
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Candidate
from devilry.devilry_group.models import FeedbackSet, FeedbacksetPassedPreviousPeriod


class PassedInPreviousPeriodError(ValidationError):
    pass


class FeedbackSetIsAlreadyGraded(PassedInPreviousPeriodError):
    """
    Will be raised when a candidate is graded on the current assignment
    """


class SomeCandidatesDoesNotQualifyToPass(PassedInPreviousPeriodError):
    """
    Will be raised when one or more candidates passed into :meth:`.PassedInPreviousPeriod.set_passed_in_current_period`
    does not qualify to pass the assignment.
    see meth:`.PassedInPreviousPeriod.get_queryset` the passed candidates will be crosschecked against the queryset
    on submit.
    """


class NoCandidatesPassed(PassedInPreviousPeriodError):
    """
    Will be raised when there is no candidates in queryset
    passed into :meth:`.PassedInPreviousPeriod.set_passed_in_current_period`
    """


class PassedInPreviousPeriod(object):

    #: Supported grading plugins is passfailed and points
    SUPPORTED_GRADING_PLUGINS = [
        Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED,
        Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS
    ]

    def __init__(self, assignment, from_period):
        """
        Initialize with assignment and the earliest period we will approve for.
        Args:
            assignment: :class:`core.Assignment`
            from_period: :class:`core.Period`
        """
        self.assignment = assignment
        self.from_period = from_period

    def get_queryset(self):
        """
        Gets the queryset for Candidates in previous periods that have passed the assignment,
        1.  Get all feedbacksets that have passed the assignment in previous periods,
                and exclude feedbacksets in current period
        2. Get all the assignment groups that have passed after ``self.from_period.start_time``
        3. Get students on current assignment ``self.assignment`` and filter away candidates who have been graded.
        4. Get all :class:`core.Candidate` objects that have passed the assignment in previous periods,
                and ensure that the newest feedback is taken in account.
        Returns:
            :class:`core.Candidate` queryset

        """
        feedbackset_queryset = FeedbackSet.objects.filter(
            group__parentnode__short_name=self.assignment.short_name,
            grading_published_datetime__isnull=False,
            group__parentnode__passing_grade_min_points__lte=models.F('grading_points')
        ).exclude(group__parentnode=self.assignment)\
            .select_related('group__parentnode')

        group_queryset = AssignmentGroup.objects.filter(
            parentnode__grading_system_plugin_id__in=self.SUPPORTED_GRADING_PLUGINS,
            parentnode__parentnode__start_time__gte=self.from_period.start_time,
            parentnode__short_name=self.assignment.short_name,
            parentnode__parentnode__start_time__lt=self.assignment.parentnode.start_time,
            cached_data__last_published_feedbackset__in=feedbackset_queryset
        ).select_related('parentnode__parentnode', 'cached_data__last_published_feedbackset')

        students_on_current = Candidate.objects.filter(
            assignment_group__parentnode=self.assignment,
            assignment_group__cached_data__last_published_feedbackset__isnull=True
        ).select_related('assignment_group__parentnode', 'relatedstudent__user')\
            .values_list('relatedstudent__user', flat=True).distinct()

        candidates = Candidate.objects.filter(
            assignment_group__in=group_queryset,
            relatedstudent__user__in=students_on_current
        ).select_related('relatedstudent__user',
                         'assignment_group__parentnode__parentnode',
                         'assignment_group__cached_data')\
            .order_by('relatedstudent__user', '-assignment_group__parentnode__publishing_time')\
            .distinct('relatedstudent__user')
        return candidates

    def get_current_candidate_queryset(self, candidates):
        """
        Gets a queryset with candidates :class:`core.Candidate` on current assignment ``self.assignment``

        Args:
            candidates: :class:`core.Candidate` candidates from previous assignments

        Returns:
            candidate queryset on current assignment

        Raises:
            :class:`.SomeCandidatesDoesNotQualifyToPass`
                raises when one or more candidates does not qualify to pass the assignment
        """
        selected_candidate_users = candidates.values_list('relatedstudent__user', flat=True)
        if (self.get_queryset().filter(relatedstudent__user__in=selected_candidate_users).count() !=
                len(selected_candidate_users)):
            raise SomeCandidatesDoesNotQualifyToPass('Some of the selected students did not qualify to pass')

        return Candidate.objects.filter(
            assignment_group__parentnode=self.assignment,
            relatedstudent__user__in=selected_candidate_users
        ).select_related('assignment_group',
                         'relatedstudent',
                         'assignment_group__cached_data__first_feedbackset')\
            .order_by('relatedstudent__user')

    def convert_points(self, old_feedbackset):
        """
        Converts the points in ``old_feedbackset`` to current grading configuration in ``self.assignment``.
        Decimals will be rounded up to give favor for the student.

        Args:
            old_feedbackset: :class:`devilry_group.FeedbackSet`

        Returns:
            Converted points.
        """
        old_grading_points = old_feedbackset.grading_points
        old_passing_grade_min_points = old_feedbackset.group.parentnode.passing_grade_min_points
        old_max_points = old_feedbackset.group.parentnode.max_points

        new_passing_grade_min_points = self.assignment.passing_grade_min_points
        new_max_points = self.assignment.max_points

        if old_max_points == old_grading_points:
            return new_max_points

        old_range = old_max_points - old_passing_grade_min_points
        new_range = new_max_points - new_passing_grade_min_points

        new_grading_points = ((old_grading_points - old_passing_grade_min_points) * new_range)
        new_grading_points = new_grading_points / float(old_range) if old_range > 0 else + 0
        new_grading_points = math.ceil(new_grading_points + new_passing_grade_min_points)

        return new_grading_points if new_grading_points <= new_max_points else new_max_points

    def __create_feedbackset_passed_previous_period(self, old_candidate, new_candidate):
        """
        Creates a :class:`devilry_group.FeedbacksetPassedPreviousPeriod` model which contains
        information about the passed assignment in previous period.

        Args:
            old_candidate: :class:`core.Candidate` the old candidate
            new_candidate: :class:`core.Candidate` new candidate in current period
        """
        old_assignment = old_candidate.assignment_group.parentnode
        old_feedbackset = old_candidate.assignment_group.cached_data.last_feedbackset
        old_period = old_candidate.assignment_group.parentnode.parentnode

        FeedbacksetPassedPreviousPeriod(
            feedbackset=new_candidate.assignment_group.cached_data.first_feedbackset,
            assignment_short_name=old_assignment.short_name,
            assignment_long_name=old_assignment.long_name,
            assignment_max_points=old_assignment.max_points,
            assignment_passing_grade_min_points=old_assignment.passing_grade_min_points,
            period_short_name=old_period.short_name,
            period_long_name=old_period.long_name,
            period_start_time=old_period.start_time,
            period_end_time=old_period.end_time,
            grading_points=old_feedbackset.grading_points,
            grading_published_by=old_feedbackset.grading_published_by,
            grading_published_datetime=old_feedbackset.grading_published_datetime
        ).save()

    def __publish_grading_on_current_assignment(self, old_candidate, new_candidate, published_by):
        """
        Publish grading on current assignment ``self.assignment``

        Args:
            old_candidate: :class:`core.Candidate` the candidate in the previous passed assignment
            new_candidate: :class:`core.Candidate` the candidate in the current period on assignment
            published_by: will be published by this user
        """
        grading_points = self.convert_points(old_candidate.assignment_group.cached_data.last_feedbackset)
        new_candidate.assignment_group.cached_data.first_feedbackset.publish(published_by, grading_points)

    def __set_passed(self, old_candidate, new_candidate, published_by):
        """
        Publishes the :class:`devilry_group.FeedbackSet` in current period with grading
        from previous period

        Args:
            old_candidate: :class:`core.Candidate` the candidate in the previous passed assignment
            new_candidate: :class:`core.Candidate` the candidate in the current period on assignment
            published_by: will be published by this user
        """
        if new_candidate.relatedstudent.user_id != old_candidate.relatedstudent.user_id:
            raise
        self.__create_feedbackset_passed_previous_period(old_candidate, new_candidate)
        self.__publish_grading_on_current_assignment(old_candidate, new_candidate, published_by)

    def set_passed_in_current_period(self, candidates, published_by):
        """
        Takes a candidate queryset with candidates that will pass the assignment in current period

        Args:
            candidates: :class:`core.Candidate` queryset with selected candidates
                that will pass the assignment in current period
            published_by: will be published by this user
        """
        if candidates.count() < 1:
            raise NoCandidatesPassed('candidate queryset is empty!')

        old_candidates_dict = {}
        for candidate in candidates:
            old_candidates_dict[candidate.relatedstudent.user_id] = candidate

        with transaction.atomic():
            for new_candidate in self.get_current_candidate_queryset(candidates):
                self.__set_passed(old_candidates_dict[new_candidate.relatedstudent.user_id],
                                  new_candidate, published_by)
