from devilry.devilry_qualifiesforexam.pluginhelpers import PluginResultsFailedVerification
from devilry.devilry_qualifiesforexam.pluginhelpers import PeriodResultsCollector

from .models import SubsetPluginSetting


class PeriodResultsCollectorAll(PeriodResultsCollector):
    def student_qualifies_for_exam(self, aggregated_relstudentinfo):
        for grouplist in aggregated_relstudentinfo.iter_groups_by_assignment():
            feedback = grouplist.get_feedback_with_most_points()
            if not feedback or not feedback.is_passing_grade:
                return False
        return True

def post_statussave_all(status, settings=None):
    qualified_now = set(PeriodResultsCollectorAll().get_relatedstudents_that_qualify_for_exam(status.period))
    qualified_saved = set([s.relatedstudent.id for s in status.get_qualified_students()])
    if qualified_now != qualified_saved:
        raise PluginResultsFailedVerification()




class PeriodResultsCollectorSubset(PeriodResultsCollector):
    def __init__(self, assignmentids_that_must_be_passed):
        self.assignmentids_that_must_be_passed = assignmentids_that_must_be_passed

    def student_qualifies_for_exam(self, aggregated_relstudentinfo):
        for assignmentid, grouplist in aggregated_relstudentinfo.assignments.iteritems():
            if assignmentid in self.assignmentids_that_must_be_passed:
                feedback = grouplist.get_feedback_with_most_points()
                if not (feedback and feedback.is_passing_grade):
                    return False
        return True

def post_statussave_subset(status, settings):
    assignmentids_that_must_be_passed = settings['assignmentids_that_must_be_passed']

    # Verify
    qualified_now = set(PeriodResultsCollectorSubset(assignmentids_that_must_be_passed).get_relatedstudents_that_qualify_for_exam(status.period))
    qualified_saved = set([s.relatedstudent.id for s in status.get_qualified_students()])
    if qualified_now != qualified_saved:
        raise PluginResultsFailedVerification()

    # Save settings
    subset = SubsetPluginSetting.objects.create(status=status)
    for assignmentid in assignmentids_that_must_be_passed:
        subset.selectedassignment_set.create(assignment_id=assignmentid)
