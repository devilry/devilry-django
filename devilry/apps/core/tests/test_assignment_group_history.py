from model_mommy import mommy
from django.utils.timezone import datetime, timedelta
from devilry.apps.core.models import AssignmentGroupHistory
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from django.test import TestCase


class TestAssignmentGroupHistory(TestCase):

    def setUp(self):
        def setUp(self):
            AssignmentGroupDbCacheCustomSql().initialize()

    def test_merge_history_meta_data(self):
        assignment_group_history = mommy.make('core.AssignmentGroupHistory')
        datetime1 = (datetime.now() - timedelta(days=1)).isoformat()
        datetime2 = (datetime.now() - timedelta(days=2)).isoformat()
        assignment_group_history.merge_history = {
                'merge_datetime': datetime1,
                'state': None,
                'from': {
                    'merge_datetime': datetime2,
                    'state': {
                        'name': 'group3'
                    },
                    'from': {
                        'merge_datetime': None,
                        'state': {
                            'name': 'group1'
                        }
                    },
                    'to': {
                        'merge_datetime': None,
                        'state': {
                            'name': 'group2'
                        }
                    }
                },
                'to': {
                    'merge_datetime': None,
                    'state': {
                        'name': 'group4'
                    }
                }
            }

        meta_data = assignment_group_history.meta_data
        self.assertEqual(len(meta_data), 2)
        self.assertDictEqual(meta_data[0], {
            'merge_datetime': datetime1,
            'from_name': 'group3',
            'to_name': 'group4'
        })
        self.assertDictEqual(meta_data[1], {
            'merge_datetime': datetime2,
            'from_name': 'group1',
            'to_name': 'group2'
        })

    def test_merge_history_meta_data_real_groups(self):
        test_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group1')
        group2 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group2')
        group3 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group3')
        group4 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group4')

        group1.merge_into(group2)
        group3.merge_into(group4)

        group4.merge_into(group2)

        meta_data = group2.assignmentgrouphistory.meta_data
        self.assertEqual(len(meta_data), 3)
        self.assertDictContainsSubset({
            'from_name': 'group4',
            'to_name': 'group2'
        }, meta_data[0])
        self.assertDictContainsSubset({
            'from_name': 'group3',
            'to_name': 'group4'
        }, meta_data[1])
        self.assertDictContainsSubset({
            'from_name': 'group1',
            'to_name': 'group2'
        }, meta_data[2])

    def test_merge_single_assignment_groups(self):
        test_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group1')
        group2 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group2')

        group1.merge_into(group2)
        self.assertEqual(group2.assignmentgrouphistory.merge_history['to']['state']['name'], 'group2')
        self.assertEqual(group2.assignmentgrouphistory.merge_history['from']['state']['name'], 'group1')

    def test_merge_assignmentgroup_multiple_times(self):
        test_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group1')
        group2 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group2')
        group3 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group3')
        group4 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group4')

        group1.merge_into(group2)
        group3.merge_into(group4)

        group4.merge_into(group2)

        group2history = group2.assignmentgrouphistory.merge_history
        self.assertIsNone(group2history['state'])
        self.assertEqual(group2history['from']['state']['name'], 'group4')
        self.assertEqual(group2history['from']['to']['state']['name'], 'group4')
        self.assertEqual(group2history['from']['from']['state']['name'], 'group3')
        self.assertEqual(group2history['to']['state']['name'], 'group2')
        self.assertEqual(group2history['to']['from']['state']['name'], 'group1')
        self.assertEqual(group2history['to']['to']['state']['name'], 'group2')

    def test_is_deleted_after_merge(self):
        test_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group1')
        group2 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group2')
        group3 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group3')
        group4 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group4')

        group1.merge_into(group2)
        historygroup2id = group2.assignmentgrouphistory.id
        group3.merge_into(group4)
        historygroup4id = group4.assignmentgrouphistory.id
        group4.merge_into(group2)

        with self.assertRaises(AssignmentGroupHistory.DoesNotExist):
            AssignmentGroupHistory.objects.get(id=historygroup4id)
        self.assertTrue(AssignmentGroupHistory.objects.filter(id=historygroup2id).exists())
