from django import test
from model_bakery import baker

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestAssignmentGroupInsertTriggers(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_create_group_creates_first_feedbackset(self):
        group = baker.make('core.AssignmentGroup')
        self.assertEqual(group.feedbackset_set.count(), 1)
