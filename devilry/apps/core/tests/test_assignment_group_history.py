from model_mommy import mommy
from django.utils.timezone import datetime, timedelta

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import AssignmentGroupHistory
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from django.test import TestCase


class TestAssignmentGroupHistory(TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_merge_history_meta_data(self):
        assignment_group_history = mommy.make('core.AssignmentGroupHistory')
        datetime1 = (datetime.now() - timedelta(days=1)).isoformat()
        datetime2 = (datetime.now() - timedelta(days=2)).isoformat()
        assignment_group_history.merge_history = {
                'merge_datetime': datetime1,
                'state': None,
                'groups': [
                    {
                        'merge_datetime': datetime2,
                        'state': {
                            'name': 'group1'
                        },
                        'groups': [
                            {
                                'merge_datetime': None,
                                'state': {
                                    'name': 'group1'
                                },
                                'groups': []
                            },
                            {
                                'merge_datetime': None,
                                'state': {
                                    'name': 'group3'
                                },
                                'groups': []
                            },
                            {
                                'merge_datetime': None,
                                'state': {
                                    'name': 'group4'
                                },
                                'groups': []
                            }
                        ]
                    },
                    {
                        'merge_datetime': None,
                        'state': {
                            'name': 'group2'
                        },
                        'groups': []
                    }
                ]
            }

        meta_data = assignment_group_history.meta_data
        self.assertEqual(len(meta_data), 2)
        self.assertDictEqual(meta_data[0], {
            'merge_datetime': datetime1,
            'groups': ['group1', 'group2']
        })
        self.assertDictEqual(meta_data[1], {
            'merge_datetime': datetime2,
            'groups': ['group1', 'group3', 'group4']
        })

    def test_merge_history_meta_data_real_groups(self):
        test_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group1')
        group2 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group2')
        group3 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group3')
        group4 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group4')

        AssignmentGroup.merge_groups([group1, group2, group3])
        AssignmentGroup.merge_groups([group1, group4])

        meta_data = AssignmentGroupHistory.objects.get(assignment_group__id=group1.id).meta_data
        self.assertEqual(len(meta_data), 2)
        self.assertDictContainsSubset({
            'groups': ['group1', 'group4']
        }, meta_data[0])
        self.assertDictContainsSubset({
            'groups': ['group1', 'group2', 'group3']
        }, meta_data[1])

    def test_merge_single_assignment_groups(self):
        test_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group1')
        group2 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group2')

        AssignmentGroup.merge_groups([group1, group2])
        merge_history = AssignmentGroupHistory.objects.get(assignment_group__id=group1.id).merge_history
        self.assertEqual(merge_history['groups'][0]['state']['name'], 'group1')
        self.assertEqual(merge_history['groups'][1]['state']['name'], 'group2')

    def test_merge_assignmentgroup_multiple_times(self):
        test_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group1')
        group2 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group2')
        group3 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group3')
        group4 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group4')

        core_mommy.candidate(group=group1)
        core_mommy.candidate(group=group1)
        core_mommy.candidate(group=group2)
        core_mommy.candidate(group=group3)
        core_mommy.candidate(group=group4)
        core_mommy.examiner(group=group1)
        core_mommy.examiner(group=group2)
        core_mommy.examiner(group=group2)
        core_mommy.examiner(group=group3)
        group1_state = group1.get_current_state()
        group2_state = group2.get_current_state()
        group3_state = group3.get_current_state()
        group4_state = group4.get_current_state()

        AssignmentGroup.merge_groups([group1, group3])
        AssignmentGroup.merge_groups([group2, group4])

        group1_merge_history = AssignmentGroupHistory.objects.get(assignment_group__id=group1.id).merge_history
        group2_merge_history = AssignmentGroupHistory.objects.get(assignment_group__id=group2.id).merge_history
        self.assertDictEqual(group1_merge_history['groups'][0]['state'], group1_state)
        self.assertDictEqual(group1_merge_history['groups'][1]['state'], group3_state)
        self.assertDictEqual(group2_merge_history['groups'][0]['state'], group2_state)
        self.assertDictEqual(group2_merge_history['groups'][1]['state'], group4_state)
        group1 = AssignmentGroup.objects.get(id=group1.id)
        group2 = AssignmentGroup.objects.get(id=group2.id)

        # Checking one more level in the Btree
        group1_state = AssignmentGroup.objects.get(id=group1.id).get_current_state()
        group2_state = AssignmentGroup.objects.get(id=group2.id).get_current_state()
        AssignmentGroup.merge_groups([group1, group2])
        group1_merge_history_new = AssignmentGroupHistory.objects.get(assignment_group__id=group1.id).merge_history
        self.assertListEqual(group1_merge_history_new['groups'][0]['groups'], group1_merge_history['groups'])
        self.assertListEqual(group1_merge_history_new['groups'][1]['groups'], group2_merge_history['groups'])
        self.assertDictEqual(group1_merge_history_new['groups'][0]['state'], group1_state)
        self.assertDictEqual(group1_merge_history_new['groups'][1]['state'], group2_state)

    def test_is_deleted_after_merge(self):
        test_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group1')
        group2 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group2')
        group3 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group3')
        group4 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group4')

        AssignmentGroup.merge_groups([group1, group2])
        historygroup1id = group1.assignmentgrouphistory.id
        AssignmentGroup.merge_groups([group4, group3])
        historygroup4id = group4.assignmentgrouphistory.id
        AssignmentGroup.merge_groups([group1, group4])

        with self.assertRaises(AssignmentGroupHistory.DoesNotExist):
            AssignmentGroupHistory.objects.get(id=historygroup4id)
        self.assertTrue(AssignmentGroupHistory.objects.filter(id=historygroup1id).exists())

    # def test_num_queries(self):
    #     test_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
    #     group1 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group1')
    #     group2 = mommy.make('core.AssignmentGroup', parentnode=test_assignment, name='group2')
    #     group_mommy.feedbackset_new_attempt_published(group1)
    #     group_mommy.feedbackset_new_attempt_published(group1)
    #     group_mommy.feedbackset_new_attempt_published(group2)
    #     group_mommy.feedbackset_new_attempt_published(group2)
    #
    #     with self.assertNumQueries(3):
    #         AssignmentGroup.merge_groups([group1, group2])
