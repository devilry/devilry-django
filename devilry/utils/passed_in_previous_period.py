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
    pass

# class MarkAsPassedInPreviousPeriodError(Exception):
#     pass
#
# class NotInPrevious(MarkAsPassedInPreviousPeriodError):
#     pass
# class OnlyFailingInPrevious(MarkAsPassedInPreviousPeriodError):
#     pass
# class HasFeedback(MarkAsPassedInPreviousPeriodError):
#     pass
# class HasAliasFeedback(HasFeedback):
#     pass
#
# class PassingGradeOnlyInMultiCandidateGroups(MarkAsPassedInPreviousPeriodError):
#     def __init__(self, groups):
#         self.groups = groups
#         super(PassingGradeOnlyInMultiCandidateGroups, self).__init__()
#
# class NotExactlyOneCandidateInGroup(MarkAsPassedInPreviousPeriodError):
#     def __init__(self, candidatecount):
#         self.candidatecount = candidatecount
#         super(NotExactlyOneCandidateInGroup, self).__init__()


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
        3. Get students on current assignment ``self.assignment``
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
            assignment_group__parentnode=self.assignment
        ).select_related('assignment_group__parentnode', 'relatedstudent__user')\
            .values_list('relatedstudent__user', flat=True).distinct()

        candidates = Candidate.objects.filter(
            assignment_group__in=group_queryset,
            relatedstudent__user__in=students_on_current
        ).select_related('relatedstudent__user',
                         'assignment_group__parentnode',
                         'assignment_group__cached_data')\
            .order_by('relatedstudent__user', '-assignment_group__parentnode__publishing_time')\
            .distinct('relatedstudent__user')
        return candidates

    def get_current_candidate_queryset(self, candidates):
        """
        Gets a queryset with candidates :class:`core.Candidate` in current assignment ``self.assignment``

        Args:
            candidates:

        Returns:

        """
        return Candidate.objects.filter(
            assignment_group__parentnode=self.assignment,
            relatedstudent__user__in=candidates.values_list('relatedstudent__user', flat=True)
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

        new_grading_points = math.ceil((((old_grading_points - old_passing_grade_min_points)
                                         * (new_max_points - new_passing_grade_min_points))
                                        / float(old_max_points - old_passing_grade_min_points))
                                       + new_passing_grade_min_points)
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

    def __publish_grading_in_current_period(self, old_candidate, new_candidate, published_by):
        """
        Publish grading in current period

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
        if new_candidate.assignment_group.cached_data.last_published_feedbackset:
            raise FeedbackSetIsAlreadyGraded('Feedbackset is already graded')
        self.__create_feedbackset_passed_previous_period(old_candidate, new_candidate)
        self.__publish_grading_in_current_period(old_candidate, new_candidate, published_by)

    def set_passed_in_current_period(self, candidates, published_by):
        """
        Takes a candidate queryset with candidates that will pass the assignment in current period

        Args:
            candidates: :class:`core.Candidate` queryset with selected candidates
                that will pass the assignment in current period
            published_by: will be published by this user
        """
        candidates = candidates.order_by('relatedstudent__user')
        with transaction.atomic():
            for old_candidate, new_candidate in zip(candidates, self.get_current_candidate_queryset(candidates)):
                self.__set_passed(old_candidate, new_candidate, published_by)

# class MarkAsPassedInPreviousPeriod(object):
#
#     def __init__(self, assignment):
#         self.assignment = assignment
#
#     def _get_previous_periods(self):
#         period = self.assignment.parentnode
#         subject = period.parentnode
#         qry = subject.periods.filter(start_time__lt=period.start_time)
#         qry = qry.order_by('-start_time') # Order descending, so we find the newest feedback when looping
#         return [period for period in qry]
#
#     def get_previous_periods(self):
#         """
#         Get the previous periods within the subject of the ``assignment``.
#         """
#         if not hasattr(self, '_previous_periods'):
#             self._previous_periods = self._get_previous_periods()
#         return self._previous_periods
#
#     def mark_all(self, pretend=False):
#         """
#         Mark all groups in assignment. Ignores:
#
#             - Ignores groups with no candidates.
#             - Ignores groups on this assignment with more than one candidate.
#               The group from a previous period (the alias) may have multiple
#               candidates.
#
#         Collects the results in a dict with the following keys:
#
#         - ``marked``: List of marked group pairs (group, oldgroup), where
#           ``group`` is the group from the current assignment.
#         - ``ignored``: Ignored groups organized by the reason for the ignore (dict):
#             - ``multiple_candidates_in_group``: The group has multiple candidates.
#             - ``no_candidates_in_group``: The group has no candidates.
#             - ``has_alias_feedback``: The active feedback is an alias delivery.
#             - ``not_in_previous``: Not found in any previous period.
#             - ``only_failing_grade_in_previous``: Found in previous period(s), but only with failing grade.
#             - ``only_multicandidategroups_passed``: The group only matches old groups with passing grade where there are more than one candidate.
#             - ``has_feedback``: The group already has feedback.
#         """
#         ignored = {'multiple_candidates_in_group': [],
#                    'no_candidates_in_group': [],
#                    'not_in_previous': [],
#                    'only_failing_grade_in_previous': [],
#                    'only_multicandidategroups_passed': [],
#                    'has_alias_feedback': [],
#                    'has_feedback': []}
#         marked = []
#
#         for group in self.assignment.assignmentgroups.all():
#             candidates = group.candidates.all()
#             if len(candidates) == 0:
#                 ignored['no_candidates_in_group'].append(group)
#             elif len(candidates) == 1:
#                 try:
#                     if pretend:
#                         oldgroup = self.find_previously_passed_group(group)
#                     else:
#                         oldgroup = self.mark_group(group)
#                 except OnlyFailingInPrevious:
#                     ignored['only_failing_grade_in_previous'].append(group)
#                 except NotInPrevious:
#                     ignored['not_in_previous'].append(group)
#                 except PassingGradeOnlyInMultiCandidateGroups:
#                     ignored['only_multicandidategroups_passed'].append(group)
#                 except HasAliasFeedback:
#                     ignored['has_alias_feedback'].append(group)
#                 except HasFeedback:
#                     ignored['has_feedback'].append(group)
#                 else:
#                     marked.append((group, oldgroup))
#             else:
#                 ignored['multiple_candidates_in_group'].append(group)
#         return {'marked': marked,
#                 'ignored': ignored}
#
#     def mark_group(self, group, feedback=None):
#         oldgroup = None
#         if not feedback:
#             oldgroup = self.find_previously_passed_group(group)
#         self.mark_as_delivered_in_previous(group, oldgroup=oldgroup, feedback=feedback)
#         return oldgroup
#
#     def find_previously_passed_group(self, group):
#         """
#         Find the newest delivery with passing feedback for this group with
#         assignment matching ``self.assignment``.
#         """
#         candidates = group.candidates.all()
#         if len(candidates) != 1:
#             raise NotExactlyOneCandidateInGroup(len(candidates))
#         candidate = candidates[0]
#
#         if StaticFeedback.objects.filter(delivery__deadline__assignment_group=group).exists():
#             if group.feedback and group.feedback.delivery.delivery_type == deliverytypes.ALIAS:
#                 raise HasAliasFeedback()
#             else:
#                 raise HasFeedback()
#
#         candidates_from_previous = self._find_candidates_in_previous(candidate)
#         if candidates_from_previous:
#             passing_but_multigroup = []
#             for candidate in candidates_from_previous:
#                 oldgroup = candidate.assignment_group
#                 if oldgroup.feedback and oldgroup.feedback.is_passing_grade \
#                         and not oldgroup.feedback.delivery.delivery_type == deliverytypes.ALIAS:
#                     if oldgroup.candidates.count() != 1:
#                         passing_but_multigroup.append(oldgroup)
#                     else:
#                         return oldgroup
#             if passing_but_multigroup:
#                 raise PassingGradeOnlyInMultiCandidateGroups(passing_but_multigroup)
#             raise OnlyFailingInPrevious()
#         else:
#             raise NotInPrevious()
#
#     def mark_as_delivered_in_previous(self, group, oldgroup=None, feedback=None):
#         if oldgroup:
#             oldfeedback = oldgroup.feedback
#             alias_delivery = oldfeedback.delivery
#             if not feedback:
#                 feedback = {'grade': oldfeedback.grade,
#                             'is_passing_grade': oldfeedback.is_passing_grade,
#                             'points': oldfeedback.points,
#                             'rendered_view': oldfeedback.rendered_view,
#                             'saved_by': oldfeedback.saved_by}
#         elif feedback:
#             alias_delivery = None
#         else:
#             raise ValueError('oldgroup or feedback is required arguments.')
#
#         latest_deadline = group.deadlines.order_by('-deadline')[0]
#         latest_deadline.deadline = datetime.now() + timedelta(seconds=60)
#         delivery = Delivery(
#             deadline=latest_deadline,
#             delivery_type=deliverytypes.ALIAS,
#             alias_delivery=alias_delivery)
#         delivery.set_number()
#         delivery.save()
#         if isinstance(feedback, dict):
#             feedback = delivery.feedbacks.create(**feedback)
#         else:
#             delivery.feedbacks.add(feedback)
#         delivery.full_clean() # NOTE: We have to validate after adding feedback, or the delivery will fail to validate
#         feedback.full_clean()
#         return feedback
#
#     def _find_candidates_in_previous(self, candidate):
#         matches = []
#         for period in self.get_previous_periods():
#             try:
#                 previous_candidate = Candidate.objects.get(assignment_group__parentnode__parentnode=period,
#                                                            assignment_group__parentnode__short_name=self.assignment.short_name,
#                                                            student=candidate.student)
#             except Candidate.DoesNotExist:
#                 pass
#             else:
#                 matches.append(previous_candidate)
#         return matches
