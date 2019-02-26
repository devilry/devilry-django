# -*- coding: utf-8 -*-


# Devilry imports
from devilry.devilry_qualifiesforexam.utils.groups_groupedby_relatedstudent_and_assignments import \
    GroupsGroupedByRelatedStudentAndAssignment


class PeriodResultsCollector(object):
    """
    Collects the results on a period for students.

    This class must be subclassed for each plugin handling it's requirement for qualifying students.
    """
    def __init__(self, period, qualifying_assignment_ids=None):
        """
        Args:
            period: The period the results are collected for.
            qualifying_assignment_ids: IDs for the Assignments as student is required to
                pass to be able to qualify for final exam.
        """
        self.period = period
        self.qualifying_assignment_ids = qualifying_assignment_ids or []
        self.grouper = GroupsGroupedByRelatedStudentAndAssignment(
            self.period,
        )

    def student_qualifies_for_exam(self, aggregated_relstudentinfo):
        """
        This function is specific for the plugin and must be implemented by a subclass.

        Args:
            aggregated_relstudentinfo: Object with assignmentinfo for student on period.

        Returns:
            bool: Student qualifies or not.
        """
        raise NotImplementedError()

    def get_relatedstudents_that_qualify_for_exam(self):
        """
        Get list of all relatedstudent IDs for all students that qualify for the exam.

        Returns:
            list: A list of :obj:`~.devilry.apps.core.models.RelatedStudent.id`s.

        """
        passing_relatedstudentids = []
        for aggregated_relstudentinfo in self.grouper.iter_relatedstudents_with_results():
            if self.student_qualifies_for_exam(aggregated_relstudentinfo):
                passing_relatedstudentids.append(aggregated_relstudentinfo.relatedstudent.id)
        return passing_relatedstudentids
