from devilry.devilry_qualifiesforexam.pluginhelpers import PluginResultsFailedVerification
from devilry.devilry_qualifiesforexam.pluginhelpers import PeriodResultsCollector

from .models import PointsPluginSetting


class PeriodResultsCollectorPoints(PeriodResultsCollector):
    def __init__(self, assignmentids, minimum_points):
        self.assignmentids = assignmentids
        self.minimum_points = minimum_points

    def student_qualifies_for_exam(self, aggregated_relstudentinfo):
        points = 0
        for assignmentid, grouplist in aggregated_relstudentinfo.assignments.iteritems():
            if assignmentid in self.assignmentids:
                feedback = grouplist.get_feedback_with_most_points()
                if feedback:
                    points += feedback.points
        return points >= self.minimum_points


def post_statussave(status, settings):
    """
    Get settings from session, and store them in a settings-object that has a
    foreign-key to the status-object.
    """
    assignmentids = settings['assignmentids']
    minimum_points = settings['minimum_points']

    # Verify
    collector = PeriodResultsCollectorPoints(assignmentids, minimum_points)
    qualified_now = set(collector.get_relatedstudents_that_qualify_for_exam(status.period))
    qualified_saved = set([s.relatedstudent.id for s in status.get_qualified_students()])
    if qualified_now != qualified_saved:
        raise PluginResultsFailedVerification()

    # Save settings
    settings = PointsPluginSetting(
            status=status,
            minimum_points=minimum_points)
    settings.full_clean()
    settings.save()
    for assignmentid in assignmentids:
        settings.pointspluginselectedassignment_set.create(assignment_id=assignmentid)
