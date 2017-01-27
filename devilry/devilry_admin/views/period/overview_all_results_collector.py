from __future__ import unicode_literals

from collections import OrderedDict

from django.db import models

from devilry.apps.core import models as core_models


class RelatedStudentResults(object):
    """
    Class encapsulates grading results for a RelatedStudent
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

    def get_result_for_assignment(self, assignment_id):
        """
        Get the result of the RelatedStudent on Assignment.

        Args:
            assignment_id: id of the Assignment to get the result for.

        Returns:
            (int or None): If the last FeedbackSet is published, the grading points are returned.
                If the student has no published feedbacksets, none is returned.
        """
        cached_data = self.cached_data_dict[assignment_id]
        if not cached_data.last_published_feedbackset:
            return None
        return cached_data.last_published_feedbackset.grading_points

    def get_total_result(self):
        """
        Count the total number of points a student has for the period.

        Returns:
            (int): total number of grading points.
        """
        total = 0
        for cached_data in self.cached_data_dict.values():
            total += cached_data.last_published_feedbackset.grading_points
        return total

    def __serialize_user(self):
        user = self.relatedstudent.user
        return {
            'id': user.id,
            'shortname': user.shortname,
            'fullname': user.fullname
        }

    def __serialize_assignment_results(self):
        assignment_result_list = []
        for assignment_id in self.cached_data_dict.keys():
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
        print self.relatedstudent.user.fullname
        for assignment_id, cached_data in self.cached_data_dict.items():
            published_feedbackset = cached_data.last_published_feedbackset
            passing_grade = cached_data.group.parentnode.points_is_passing_grade(published_feedbackset.grading_points)
            print '    - Assignment {} ({}):\n        * Points: {}/{} (passed: {})'.format(
                assignment_id,
                cached_data.group.parentnode,
                cached_data.last_published_feedbackset.grading_points,
                cached_data.group.parentnode.max_points,
                passing_grade
            )


class PeriodAllResultsCollector(object):
    """
    Collects information about RelatedStudents and builds a structure containing
    the information needed.
    """
    def __init__(self, period):
        #: The period the result info gathering is for.
        self.period = period

        #: A dictionary with results for all RelatedStudents, where the key is the RelatedStudent.id
        #: and the value is an instance of RelatedStudentResults.
        self.results = {}

        self.__initialize_results()

    def __get_candidate_queryset(self):
        """
        Get a queryset of Candidates with prefetched groups and results.

        Returns:
            (QuerySet): a QuerySet of candidates.
        """
        return core_models.Candidate.objects\
            .select_related(
                'assignment_group',
                'assignment_group__parentnode',
                'assignment_group__parentnode__parentnode',
                'assignment_group__parentnode__parentnode__parentnode',
                'assignment_group__cached_data',
                'assignment_group__cached_data__last_published_feedbackset')

    def __get_relatedstudents(self):
        """
        Get all RelatedStudents for the period.

        Returns:
            (QuerySet): QuerySet of RelatedStudents.
        """
        relatedstudent_queryset = core_models.RelatedStudent.objects\
            .filter(period=self.period)\
            .select_related('period', 'user')\
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

    def serialize_all_results(self):
        serialized = {
            'relatedstudents': [result_info.serialize() for result_info in self.results.itervalues()]
        }
        return serialized

    def prettyprint_all_results(self):
        """
        Pretty prints the result on all Assignments for each RelatedStudent.
        """
        for relatedstudent_id, relatedstudent_results in self.results.items():
            relatedstudent_results.prettyprint_results()
            print '\n'
