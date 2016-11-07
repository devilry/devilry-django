# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Devilry imports
from devilry.devilry_qualifiesforexam.utils.groups_groupedby_relatedstudent_and_assignments import \
    GroupsGroupedByRelatedStudentAndAssignment


class PeriodResultsCollector(object):
    """
    Collects the results on a period for students.
    """

    def __init__(self, period, qualifying_assignment_ids=None):
        """
        Args:
            period: The period the results are collected for.
        """
        self.period = period
        self.qualifying_assignment_ids = qualifying_assignment_ids

    def student_qualifies_for_exam(self, aggregated_relstudentinfo):
        """
        This function is specific for the plugin and must be implemented by a subclass.

        Args:
            aggregated_relstudentinfo: Object with assignmentinfo for student on period.

        Returns:
            bool: Student qualifies or not.
        """
        raise NotImplementedError()

    def get_aggregated_relatedstudentinfo_list(self):
        """
        Get a list of :class:`AggregatedRelatedStudentInfo` objects.
        """
        grouper = GroupsGroupedByRelatedStudentAndAssignment(period=self.period)
        studentinfo_list = []
        for relatedstudent_id, aggregatedstudentinfo in grouper.result.iteritems():
            studentinfo_list.append(aggregatedstudentinfo)
        return studentinfo_list

    def get_related_students_results(self):
        """
        Get dictionary with relatedstudent.id as key and :class:`AggregatedRelatedStudentInfo` as value.
        """
        grouper = GroupsGroupedByRelatedStudentAndAssignment(
                period=self.period,
                qualifying_assignment_ids=self.qualifying_assignment_ids)
        return grouper.result
