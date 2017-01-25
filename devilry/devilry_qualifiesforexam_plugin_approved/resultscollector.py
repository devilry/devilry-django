# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Devilry imports
from devilry.devilry_qualifiesforexam.pluginhelpers import PeriodResultsCollector


class PeriodResultSetCollector(PeriodResultsCollector):
    """
    A subset of assignments are evaluated for the period.
    """
    def student_qualifies_for_exam(self, aggregated_relstudentinfo):
        for assignmentid, groupfeedbacksetlist in aggregated_relstudentinfo.assignments.iteritems():
            if assignmentid in self.qualifying_assignment_ids or len(self.qualifying_assignment_ids) == 0:
                feedbackset = groupfeedbacksetlist.get_feedbackset_with_most_points()
                if not feedbackset:
                    return False
                elif feedbackset.grading_points < feedbackset.group.parentnode.passing_grade_min_points:
                    return False
        return True
