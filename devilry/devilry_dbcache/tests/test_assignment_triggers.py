from django import test
from model_mommy import mommy

from devilry.apps.core.mommy_recipes import ASSIGNMENT_ACTIVEPERIOD_START_FIRST_DEADLINE
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestAssignmentTriggers(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_autocreated_feedbackset_has_deadline_datetime_from_assignment(self):
        assignment = mommy.make(
            'core.Assignment',
            first_deadline=ASSIGNMENT_ACTIVEPERIOD_START_FIRST_DEADLINE)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        first_feedbackset = group.feedbackset_set.first()
        self.assertEqual(first_feedbackset.deadline_datetime, ASSIGNMENT_ACTIVEPERIOD_START_FIRST_DEADLINE)

    def test_autocreated_first_feedbackset_after_delete_has_deadline_datetime_from_assignment(self):
        assignment = mommy.make(
            'core.Assignment',
            first_deadline=ASSIGNMENT_ACTIVEPERIOD_START_FIRST_DEADLINE)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        first_feedbackset = group.feedbackset_set.first()
        self.assertEqual(first_feedbackset.deadline_datetime, ASSIGNMENT_ACTIVEPERIOD_START_FIRST_DEADLINE)
