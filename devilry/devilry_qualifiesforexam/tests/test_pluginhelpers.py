# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# 3rd party imports
from model_mommy import mommy

# Python imports
import unittest

# Django import
from django import test

# Devilry imports
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.project.common import settings
from devilry.devilry_qualifiesforexam.utils import groups_groupedby_relatedstudent_and_assignments
from devilry.devilry_qualifiesforexam import pluginhelpers
from devilry.apps.core import models as core_models
from devilry.devilry_group import devilry_group_mommy_factories


class TestPluginHelper:

    def _build_data_set(self, grading_plugin=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED,
                        min_points=1,
                        max_points=1):
        """
        Creates a default dataset for a Period with:
        3 Assignments,
        1 AssignmentGroup for each Assignment,
        1 FeedbackSet for each AssignmentGroup
        1 user,
        1 RelatedStudent,
        1 Candidate for each AssignmentGroup linked to the RelatedStudent.

        Returns:
            dict: Dictionary of all database entries to make it easier to add or remove stuff based
                on the specification of the test.

        """
        # Util function for creating a dataset of multiple assignments
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        admin_user = mommy.make(settings.AUTH_USER_MODEL)
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup', period=testperiod)
        mommy.make('devilry_account.PermissionGroupUser',
                   user=admin_user,
                   permissiongroup=periodpermissiongroup.permissiongroup)

        # Create assignments
        assign1 = mommy.make('core.Assignment',
                             short_name='assignment1',
                             long_name='Assignment 1',
                             parentnode=testperiod,
                             grading_system_plugin_id=grading_plugin,
                             max_points=max_points,
                             passing_grade_min_points=min_points)
        assign2 = mommy.make('core.Assignment',
                             short_name='assignment2',
                             long_name='Assignment 2',
                             parentnode=testperiod,
                             grading_system_plugin_id=grading_plugin,
                             max_points=max_points,
                             passing_grade_min_points=min_points)
        assign3 = mommy.make('core.Assignment',
                             short_name='assignment3',
                             long_name='Assignment 3',
                             parentnode=testperiod,
                             grading_system_plugin_id=grading_plugin,
                             max_points=max_points,
                             passing_grade_min_points=min_points)

        # Create AssignmentGroups
        assigngroup1 = mommy.make('core.AssignmentGroup', parentnode=assign1)
        assigngroup2 = mommy.make('core.AssignmentGroup', parentnode=assign2)
        assigngroup3 = mommy.make('core.AssignmentGroup', parentnode=assign3)

        # Create FeedbackSets
        fb1 = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=assigngroup1,
                grading_points=1)
        fb2 = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=assigngroup2,
                grading_points=1)
        fb3 = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=assigngroup3,
                grading_points=1)

        # Create a student with user
        student_user = mommy.make(settings.AUTH_USER_MODEL, shortname='apduc', fullname='April Duck')
        relatedstudent = mommy.make('core.RelatedStudent', user=student_user, period=testperiod)

        # Create candidates with relatedstudents and assignmentgroups
        cand1 = mommy.make('core.Candidate', relatedstudent=relatedstudent, assignment_group=assigngroup1)
        cand2 = mommy.make('core.Candidate', relatedstudent=relatedstudent, assignment_group=assigngroup2)
        cand3 = mommy.make('core.Candidate', relatedstudent=relatedstudent, assignment_group=assigngroup3)

        return {'testperiod': testperiod,
                'testassignments': [assign1, assign2, assign3],
                'testgroups': [assigngroup1, assigngroup2, assigngroup3],
                'testcandidates': [cand1, cand2, cand3],
                'testfeedbacksets': [fb1, fb2, fb3],
                'relatedstudent': relatedstudent,
                'student_user': student_user,
                'admin_user': admin_user
                }


class TestGroupFeedbackSetList(test.TestCase, TestPluginHelper):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_append_errorhandling_not_a_tuple(self):
        # Test that adding something not a tuple will raise a ValueError.
        groupfeedbacksetlist = groups_groupedby_relatedstudent_and_assignments.GroupFeedbackSetList()
        with self.assertRaisesMessage(ValueError, 'Appended object must be a tuple of '
                                                  'objects (AssignmentGroup, FeedbackSet).'):
            groupfeedbacksetlist.append(1)

    def test_append_errorhandling_not_supported_objects(self):
        # Test that adding a tuple with objects not of the required type will raise a ValueError.
        groupfeedbacksetlist = groups_groupedby_relatedstudent_and_assignments.GroupFeedbackSetList()
        with self.assertRaisesMessage(ValueError, 'Objects in tuple must be of (AssignmentGroup, FeedbackSet) '
                                                  'in that order.'):
            groupfeedbacksetlist.append((1, 1))

    def test_serialize_feedbackset(self):
        # Test serialization of feedbackset.

        # Create FeedbackSet
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                grading_points=1,
                grading_published_by=mommy.make(settings.AUTH_USER_MODEL, shortname='donduc', fullname='Donald Duck')
        )

        groupfeedbacksetlist = groups_groupedby_relatedstudent_and_assignments.GroupFeedbackSetList()
        serialized_feedbackset = groupfeedbacksetlist._serialize_feedbackset(feedbackset)

        self.assertEquals(serialized_feedbackset['id'], feedbackset.id)
        self.assertEquals(serialized_feedbackset['grade'], 'NA')
        self.assertEquals(serialized_feedbackset['points'], feedbackset.grading_points)
        self.assertEquals(serialized_feedbackset['published_by'], feedbackset.grading_published_by)
        self.assertEquals(serialized_feedbackset['published'], feedbackset.grading_published_datetime)
        self.assertEquals(serialized_feedbackset['deadline'], feedbackset.current_deadline())

    def test_serialize_group(self):
        # Test serialization of AssignmentGroup

        # Create AssignmentGroup
        testgroup = mommy.make('core.AssignmentGroup')

        # Create FeedbackSet
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                grading_points=1,
                grading_published_by=mommy.make(settings.AUTH_USER_MODEL, shortname='donduc', fullname='Donald Duck')
        )

        groupfeedbacksetlist = groups_groupedby_relatedstudent_and_assignments.GroupFeedbackSetList()
        serialized_group = groupfeedbacksetlist._serialize_group(testgroup, feedbackset)
        self.assertEquals(serialized_group['id'], testgroup.id)
        self.assertEquals(type(serialized_group['feedbackset']), dict)
        self.assertEquals(serialized_group['status'], testgroup.get_status())

    def test_serialize(self):
        # Test serialization of the entire GroupFeedbackSetList.

        # Create AssignmentGroup
        testgroup1 = mommy.make('core.AssignmentGroup')
        testgroup2 = mommy.make('core.AssignmentGroup')

        # Create examiner
        testexaminer = mommy.make(settings.AUTH_USER_MODEL, shortname='donduc', fullname='Donald Duck')

        # Create FeedbackSet
        test_feedbackset1 = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                grading_points=1,
                grading_published_by=testexaminer,
                group=testgroup1
        )
        test_feedbackset2 = devilry_group_mommy_factories.feedbackset_first_attempt_published(
                grading_points=1,
                grading_published_by=testexaminer,
                group=testgroup2
        )

        groupfeedbacksetlist = groups_groupedby_relatedstudent_and_assignments.GroupFeedbackSetList()
        groupfeedbacksetlist.append((testgroup1, test_feedbackset1))
        groupfeedbacksetlist.append((testgroup2, test_feedbackset2))
        serialized = groupfeedbacksetlist.serialize()

        self.assertEquals(2, len(serialized))
        self.assertEquals(serialized[0]['id'], testgroup1.id)
        self.assertEquals(serialized[1]['id'], testgroup2.id)


class TestAggregatedRelatedStudentInfoSerializers(test.TestCase, TestPluginHelper):
    """
    Does some simple testing for the serialization of AggregatedRelatedStudentInfo.
    """
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_serialize_user(self):
        # Test serialization of user.
        dataset_dict = self._build_data_set()
        grouper = groups_groupedby_relatedstudent_and_assignments.GroupsGroupedByRelatedStudentAndAssignment(
            period=dataset_dict['testperiod'],
        )
        serialized_user = grouper.result.values()[0].serialize()['user']
        self.assertEquals(serialized_user['id'], dataset_dict['student_user'].id)
        self.assertEquals(serialized_user['username'], dataset_dict['student_user'].shortname)
        self.assertEquals(serialized_user['fullname'], dataset_dict['student_user'].fullname)

    def test_serialize_relatedstudent(self):
        # Test serialization of relatedstudent.
        dataset_dict = self._build_data_set()
        grouper = groups_groupedby_relatedstudent_and_assignments.GroupsGroupedByRelatedStudentAndAssignment(
            period=dataset_dict['testperiod']
        )
        serialized_relatedstudent = grouper.result.values()[0].serialize()['relatedstudent']
        self.assertEquals(serialized_relatedstudent['id'], dataset_dict['relatedstudent'].id)
        self.assertEquals(serialized_relatedstudent['tags'], dataset_dict['relatedstudent'].tags)
        self.assertEquals(serialized_relatedstudent['candidate_id'], dataset_dict['relatedstudent'].candidate_id)

    def test_serialize_groups_by_assignments(self):
        # Test the serialization of groups by assignment.
        dataset_dict = self._build_data_set()
        grouper = groups_groupedby_relatedstudent_and_assignments.GroupsGroupedByRelatedStudentAndAssignment(
            period=dataset_dict['testperiod'],
        )
        serialized_groups_by_assignment = grouper.result.values()[0].serialize()['groups_by_assignment']
        self.assertEquals(serialized_groups_by_assignment[0]['assignmentid'], dataset_dict['testassignments'][0].id)

        # Test serialized group part
        serialized_group = serialized_groups_by_assignment[0]['group_feedbackset_list'][0]
        self.assertEquals(len(serialized_groups_by_assignment[0]['group_feedbackset_list']), 1)
        self.assertEquals(serialized_group['id'], dataset_dict['testgroups'][0].id)
        self.assertEquals(serialized_group['status'], dataset_dict['testgroups'][0].get_status())

        # Test the serialized feedbackset part
        serialized_feedbackset = serialized_group['feedbackset']
        self.assertEquals(serialized_feedbackset['id'], dataset_dict['testfeedbacksets'][0].id)
        self.assertEquals(serialized_feedbackset['points'], dataset_dict['testfeedbacksets'][0].grading_points)
        self.assertEquals(serialized_feedbackset['published_by'],
                          dataset_dict['testfeedbacksets'][0].grading_published_by)
        self.assertEquals(serialized_feedbackset['published'],
                          dataset_dict['testfeedbacksets'][0].grading_published_datetime)
        self.assertEquals(serialized_feedbackset['deadline'], dataset_dict['testfeedbacksets'][0].current_deadline())


class TestGroupsGroupedByRelatedStudentAndAssignment(test.TestCase, TestPluginHelper):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_assignment_fetches_all_for_period(self):
        # Test that all Assignments for the Period is fetched when no
        # qualifying Assignments are passed to the grouper.
        dataset_dict = self._build_data_set()
        testassignments = dataset_dict['testassignments']
        grouper = groups_groupedby_relatedstudent_and_assignments.GroupsGroupedByRelatedStudentAndAssignment(
            period=dataset_dict['testperiod']
        )
        retreived_assignment_ids = [assignment.id for assignment in grouper.assignments]
        self.assertEquals(len(retreived_assignment_ids), 3)
        self.assertIn(testassignments[0].id, retreived_assignment_ids)
        self.assertIn(testassignments[1].id, retreived_assignment_ids)
        self.assertIn(testassignments[2].id, retreived_assignment_ids)

    def test_student_qualifies(self):
        dataset_dict = self._build_data_set()
        resultinfo = groups_groupedby_relatedstudent_and_assignments.GroupsGroupedByRelatedStudentAndAssignment(
            period=dataset_dict['testperiod']).result
        for aggregatedstudentinfo in resultinfo.itervalues():
            self.assertTrue(aggregatedstudentinfo.student_qualifies())

    def test_student_does_not_qualify_not_enlisted(self):
        # Tests that a student does not qualify when not enlisted on a qualifying Assignment.
        dataset_dict = self._build_data_set()
        dataset_dict['testcandidates'][2].delete()
        resultinfo = groups_groupedby_relatedstudent_and_assignments.GroupsGroupedByRelatedStudentAndAssignment(
            period=dataset_dict['testperiod']).result
        for aggregatedstudentinfo in resultinfo.itervalues():
            self.assertFalse(aggregatedstudentinfo.student_qualifies())

    def test_student_does_not_qualify_not_enough_points(self):
        dataset_dict = self._build_data_set()
        # Set the points to 0 on FeedbackSet for Assignment 3
        dataset_dict['testfeedbacksets'][2].grading_points = 0
        dataset_dict['testfeedbacksets'][2].save()
        resultinfo = groups_groupedby_relatedstudent_and_assignments.GroupsGroupedByRelatedStudentAndAssignment(
            period=dataset_dict['testperiod']).result
        for aggregatedstudentinfo in resultinfo.itervalues():
            self.assertFalse(aggregatedstudentinfo.student_qualifies())

    def test_student_qualifies_assignment_not_passed(self):
        # Check that a student qualifies when assignment is not passed, but assignment is
        # not part of qualifying assignments.
        dataset_dict = self._build_data_set()
        testassignments = dataset_dict['testassignments']
        resultinfo = groups_groupedby_relatedstudent_and_assignments.GroupsGroupedByRelatedStudentAndAssignment(
            period=dataset_dict['testperiod'],
        ).result
        for aggregatedstudentinfo in resultinfo.itervalues():
            self.assertTrue(aggregatedstudentinfo.student_qualifies())

    def test_student_does_not_qualify_assignment_not_published(self):
        # Tests that a student is not qualified if any of the qualifying assignments are not published.
        dataset_dict = self._build_data_set()

        # Update feedbackset to passed but not published.
        dataset_dict['testfeedbacksets'][2].grading_points = 1
        dataset_dict['testfeedbacksets'][2].grading_published_datetime = None
        dataset_dict['testfeedbacksets'][2].save()
        resultinfo = groups_groupedby_relatedstudent_and_assignments.GroupsGroupedByRelatedStudentAndAssignment(
            period=dataset_dict['testperiod']
        ).result
        for aggregatedstudentinfo in resultinfo.itervalues():
            self.assertFalse(aggregatedstudentinfo.student_qualifies())
