# -*- coding: utf-8 -*-


# Devilry imports
from devilry.devilry_qualifiesforexam.pluginhelpers import PeriodResultsCollector


class PeriodResultSetCollector(PeriodResultsCollector):
    """
    A subset or proper subset of assignments are evaluated for the period.
    """
    def __init__(self, custom_min_passing_score=None, *args, **kwargs):
        """
        Args:
            custom_min_passing_score: Custom score used if not ``None``. If this is ``None``, the sum of all
                :obj:`~.devilry.devilry.apps.core.models.Assignment.passing_grade_min_points` will for each
                qualifying assignment will be used.
            *args: See :class:`~.devilry.devilry_qualifiesforexam.pluginshelper.PeriodResultsCollector`.
            **kwargs: See :class:`~.devilry.devilry_qualifiesforexam.pluginshelper.PeriodResultsCollector`.
        """
        super(PeriodResultSetCollector, self).__init__(*args, **kwargs)
        self.min_passing_score = custom_min_passing_score or self._get_course_min_passing_score()

    def _get_course_min_passing_score(self):
        """
        Calculate minimum score needed to qualify for the final exam in course.
        Iterates through all the qualifying assignments, and calculates the max score.

        Returns:
            Max score.
        """
        min_points = 0
        for assignment in self.grouper.assignments:
            if assignment.id in self.qualifying_assignment_ids:
                min_points += assignment.passing_grade_min_points
        return min_points

    def student_qualifies_for_exam(self, aggregated_relstudentinfo):
        """
        Iterate over the information for a RelatedStudent, and summarize the points of each FeedbackSet.
        """
        accumulated_score = 0
        for assignmentid, groupfeedbacksetlist in aggregated_relstudentinfo.assignments.items():
            if assignmentid in self.qualifying_assignment_ids or len(self.qualifying_assignment_ids) == 0:
                feedbackset = groupfeedbacksetlist.get_feedbackset_with_most_points()
                if feedbackset and feedbackset.grading_points:
                    accumulated_score += feedbackset.grading_points
        return accumulated_score >= self.min_passing_score
