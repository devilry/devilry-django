

from collections import OrderedDict

from django.db import models
from django.utils import timezone

from devilry.apps.core import models as core_models


class RelatedStudentResults(object):
    """
    Class encapsulates grading results for a RelatedStudent.
    """
    def __init__(self, relatedstudent, cached_data_dict):
        #: The RelatedStudent
        self.relatedstudent = relatedstudent

        #: Dict of cached_data for each assignment, with Assignment.id as key and
        #: cached_data as the value.
        self.cached_data_dict = cached_data_dict

    def student_is_registered_on_assignment(self, assignment_id):
        """
        Check if the student is registered on the assignment

        Args:
            assignment_id: id of assignment to check.

        Returns:
            (bool): True if student is registered on assignment, else False.
        """
        try:
            self.cached_data_dict[assignment_id]
        except KeyError:
            return False
        return True

    def is_waiting_for_feedback(self, assignment_id):
        """
        Check if the student is waiting for feedback on the assignment.

        The student is waiting for feedback if registered on the ``Assignment``, but the last ``FeedbackSet``
        is not published.

        Returns:
            (bool): True if student is waiting for feedback, else false.

        Raises:
            (ValueError): If the student is not registered on the ``Assignment``.
        """
        if not self.student_is_registered_on_assignment(assignment_id=assignment_id):
            raise ValueError('You are checking if the student is waiting for feedback when the student is not '
                             'registered on the assignment. Maybe you should call '
                             'student_is_registered_on_assignment(assignment_id=) first?')
        cached_data = self.cached_data_dict[assignment_id]
        if cached_data.last_published_feedbackset_is_last_feedbackset:
            return False
        return True

    def no_deliveries_hard_deadline(self, assignment):
        """
        Check if the student has no deliveries on the last feedbackset for the assignment.

        This check differs from :meth:`.RelatedStudentResults.is_waiting_for_feedback` in that if the assignments
        deadline-handling is `HARD`, the deadline has expired and the student has no comments, then the student has no
        deliveries.

        Note: This method always returns ``False`` if the deadline-handling is not `HARD`.

        Returns:
            (bool): True if the student has no uploaded comments and the deadline expired.

        Raises:
            (ValueError): If the student is not registered on the ``Assignment``.
        """
        if not assignment.deadline_handling_is_hard():
            return False

        if not self.student_is_registered_on_assignment(assignment_id=assignment.id):
            raise ValueError('You are checking if the student is waiting for deliveries when the student is not '
                             'registered on the assignment. Maybe you should call '
                             'student_is_registered_on_assignment(assignment_id=) first?')
        cached_data = self.cached_data_dict[assignment.id]
        if self.is_waiting_for_feedback(assignment_id=assignment.id):
            if cached_data.public_student_comment_count == 0 and cached_data.public_student_file_upload_count == 0:
                return True
        return False

    def is_waiting_for_deliveries(self, assignment_id):
        """
        Check if the student still can deliver on the assignment.

        The student is waiting for deliveries if registered on the ``Assignment``, but the deadline of last
        ``FeedBackSet`` is greater than or equal to current time

        Returns:
            (bool): True if the student still can deliver to the assignment, else False

        Raises:
            (ValueError): If the student is not registered on the ``Assignment``

        """
        if not self.student_is_registered_on_assignment(assignment_id=assignment_id):
            raise ValueError('You are checking if the student is waiting for deliveries when the student is not '
                             'registered on the assignment. Maybe you should call '
                             'student_is_registered_on_assignment(assignment_id=) first?')
        cached_data = self.cached_data_dict[assignment_id]
        if cached_data.last_published_feedbackset_is_last_feedbackset:
            return False
        if cached_data.last_feedbackset_deadline_datetime < timezone.now():
            return False
        return True

    def get_result_for_assignment(self, assignment_id):
        """
        Get the result of the RelatedStudent on Assignment.

        Note::
            If the student is registered on the ``Assignment``, but the ``FeedbackSet`` is not published,
            0 is returned. The return-value would be the same if the ``FeedbackSet`` is published, but with
            ``grading_points = 0``

        Args:
            assignment_id: id of the Assignment to get the result for.

        Returns:
            (int or None): If the student is registered on the assignment, grading points or 0 is returned.
             If the student is not registered on the assignment, None is returned.
        """
        if not self.student_is_registered_on_assignment(assignment_id=assignment_id):
            return None
        cached_data = self.cached_data_dict[assignment_id]
        if not cached_data.last_published_feedbackset_is_last_feedbackset:
            return 0
        return cached_data.last_published_feedbackset.grading_points

    def get_total_result(self):
        """
        Count the total number of points a student has for the period.
        If the student has no published feedback for the assignment, this is regarded as 0 points.

        Returns:
            (int): total number of grading points.
        """
        total = 0
        for cached_data in list(self.cached_data_dict.values()):
            if cached_data.last_published_feedbackset_is_last_feedbackset:
                total += cached_data.last_published_feedbackset.grading_points
        return total

    def get_cached_data_list(self):
        """
        Get a list sorted by the current deadline of the last feedbackset for every
        AssignmentGroupCachedData.

        Returns:
            (list): Sorted list of AssignmentGroupCachedData.
        """
        cached_data_list = [cached_data for cached_data in list(self.cached_data_dict.values())]
        cached_data_list.sort(key=lambda cd: cd.group.assignment.publishing_time)
        return cached_data_list

    def __serialize_user(self):
        user = self.relatedstudent.user
        return {
            'id': user.id,
            'shortname': user.shortname,
            'fullname': user.fullname
        }

    def __serialize_assignment_results(self):
        assignment_result_list = []
        for assignment_id in list(self.cached_data_dict.keys()):
            assignment_result_list.append({
                'id': assignment_id,
                'result': self.get_result_for_assignment(assignment_id=assignment_id)
            })
        return assignment_result_list

    def serialize(self):
        return {
            'relatedstudent_id': self.relatedstudent.id,
            'user': self.__serialize_user(),
            'assignments': self.__serialize_assignment_results()
        }

    def prettyprint_results(self):
        """
        Simple prettyprint showing the results of the RelatedStudent for
        each Assignment.
        """
        for assignment_id, cached_data in list(self.cached_data_dict.items()):
            published_feedbackset = cached_data.last_published_feedbackset
            passing_grade = cached_data.group.parentnode.points_is_passing_grade(published_feedbackset.grading_points)
            print('    - Assignment {} ({}):\n        * Points: {}/{} (passed: {})'.format(
                assignment_id,
                cached_data.group.parentnode,
                cached_data.last_published_feedbackset.grading_points,
                cached_data.group.parentnode.max_points,
                passing_grade
            ))


class PeriodAllResultsCollector(object):
    """
    Collects information about RelatedStudents and builds a structure containing
    the information needed.

    Attributes:
        period (:class:`~.devilry.apps.core.models.Period`): The ``period`` to collect results for.

        related_student_ids (list): List of :attr:`~.devilry.apps.core.RelatedStudent.id`s for the students
            registered on the period.

        results (dict): Dictionary with :attr:`~.devilry.apps.core.RelatedStudent.id` as keys and an instance of
        :class:`~.RelatedStudentResults` as value for each key.
    """
    def __init__(self, period, related_student_ids):
        #: The period the result info gathering is for.
        self.period = period

        #: IDs of the ``RelatedStudents`` on the period.
        self.related_student_ids = related_student_ids

        #: A dictionary with results for all RelatedStudents, where the key is the RelatedStudent.id
        #: and the value is an instance of RelatedStudentResults.
        self.results = {}

        self.__initialize_results()

    def __get_candidate_queryset(self):
        """
        Get a queryset of ``Candidates`` with prefetched groups and results.

        Returns:
            (QuerySet): a QuerySet of :class:`~.devilry.apps.core.models.Candidate`.
        """
        return core_models.Candidate.objects\
            .select_related(
                'assignment_group',
                'assignment_group__parentnode',
                'assignment_group__parentnode__parentnode',
                'assignment_group__parentnode__parentnode__parentnode',
                'assignment_group__cached_data__last_feedbackset__group',
                'assignment_group__cached_data__last_feedbackset__group__parentnode',
                'assignment_group__cached_data__last_feedbackset',
                'assignment_group__cached_data__last_published_feedbackset')

    def __get_relatedstudents(self):
        """
        Get all ``RelatedStudents`` for the period.

        Returns:
            (QuerySet): QuerySet of :class:`~.devilry.apps.core.models.RelatedStudents`.
        """
        relatedstudent_queryset = core_models.RelatedStudent.objects\
            .filter(period=self.period)\
            .filter(id__in=self.related_student_ids)\
            .select_related('period', 'period__parentnode', 'user')\
            .prefetch_related(
                models.Prefetch(
                    'candidate_set',
                    queryset=self.__get_candidate_queryset()))
        return relatedstudent_queryset

    def __get_cached_data_dict_for_candidates(self, candidates_list):
        """
        Get a dictionary of cached_data ordered by the Assignments id.

        Args:
            candidates_list: list of candidates.

        Returns:
            (OrderedDict): ordered dict of cached_data
        """
        cached_data_dict = OrderedDict()
        for candidate in candidates_list:
            cached_data = candidate.assignment_group.cached_data
            cached_data_dict[cached_data.group.parentnode.id] = cached_data
        return cached_data_dict

    def __initialize_results(self):
        """
        Build results dictionary.
        """
        for relatedstudent in self.__get_relatedstudents():
            self.results[relatedstudent.id] = RelatedStudentResults(
                relatedstudent=relatedstudent,
                cached_data_dict=self.__get_cached_data_dict_for_candidates(
                    list(relatedstudent.candidate_set.all())
                )
            )

    def has_students(self):
        """

        Returns:

        """
        return len(self.related_student_ids) > 0

    def iter_related_student_results(self):
        """
        Get an iterator over the :obj:`~.RelatedStudentResults` on the period.

        This is convenient if you want information about each ``RelatedStudent``, and is
        a shortcut for iterating the :attr:`~.PeriodAllResultsCollector.results` dict.

        Returns:
            (iterator): iterator over :obj:`~.RelatedStudentResults`.
        """
        return iter(self.results.values())

    def serialize_all_results(self):
        serialized = {
            'relatedstudents': [result_info.serialize() for result_info in self.results.values()]
        }
        return serialized

    def prettyprint_all_results(self):
        """
        Pretty prints the result on all Assignments for each RelatedStudent.
        """
        for relatedstudent_id, relatedstudent_results in list(self.results.items()):
            relatedstudent_results.prettyprint_results()
            print('\n')
