# -*- coding: utf-8 -*-


# Devilry imports
from devilry.devilry_qualifiesforexam.pluginhelpers import PeriodResultsCollector


class PeriodResultSetCollector(PeriodResultsCollector):
    """
    All selected students qualify for the exam.
    """
    def __init__(self, qualifying_student_ids, **kwargs):
        """
        Args:
            qualifying_student_ids: IDs for the Assignments as student is required to
                pass to be able to qualify for final exam.
            **kwargs: Keyword arguments passed to the parent class.
        """
        self.qualifying_student_ids = qualifying_student_ids
        super().__init__(**kwargs)

    def student_qualifies_for_exam(self, aggregated_relstudentinfo):
        if aggregated_relstudentinfo.relatedstudent.id in self.qualifying_student_ids:
            return True
        return False
