# -*- coding: utf-8 -*-


# Django imports
from django import test

# Devilry imports
from model_bakery import baker
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.project.common import settings
from devilry.devilry_group import devilry_group_baker_factories
from devilry.apps.core import models as core_models
from devilry.devilry_qualifiesforexam.tests import test_pluginhelpers
from devilry.devilry_qualifiesforexam_plugin_points import resultscollector


class TestPeriodResultSetCollector(test.TestCase, test_pluginhelpers.TestPluginHelper):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_collector_min_passing_score_without_custom_score(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        testassignment1 = baker.make('core.Assignment', parentnode=testperiod, passing_grade_min_points=10)
        testassignment2 = baker.make('core.Assignment', parentnode=testperiod, passing_grade_min_points=10)
        testassignment3 = baker.make('core.Assignment', parentnode=testperiod, passing_grade_min_points=10)
        collector = resultscollector.PeriodResultSetCollector(period=testperiod, qualifying_assignment_ids=[
            testassignment1.id,
            testassignment2.id,
            testassignment3.id
        ])
        self.assertEqual(collector.min_passing_score, 30)

    def test_collector_min_passing_score_with_custom_score(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        testassignment1 = baker.make('core.Assignment', parentnode=testperiod, passing_grade_min_points=10)
        testassignment2 = baker.make('core.Assignment', parentnode=testperiod, passing_grade_min_points=10)
        testassignment3 = baker.make('core.Assignment', parentnode=testperiod, passing_grade_min_points=10)
        collector = resultscollector.PeriodResultSetCollector(
                custom_min_passing_score=20,
                period=testperiod,
                qualifying_assignment_ids=[
                    testassignment1.id,
                    testassignment2.id,
                    testassignment3.id
                ])
        self.assertEqual(collector.min_passing_score, 20)

    def test_student_qualify_with_all_assignments_qualify_without_custom_score(self):
        data_dict = self._build_data_set(
                grading_plugin=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
                min_points=5,
                max_points=5
        )
        data_dict['testfeedbacksets'][0].grading_points = 5
        data_dict['testfeedbacksets'][1].grading_points = 5
        data_dict['testfeedbacksets'][2].grading_points = 5
        data_dict['testfeedbacksets'][0].save()
        data_dict['testfeedbacksets'][1].save()
        data_dict['testfeedbacksets'][2].save()

        collector = resultscollector.PeriodResultSetCollector(
                period=data_dict['testperiod'],
                qualifying_assignment_ids=[
                    data_dict['testassignments'][0].id,
                    data_dict['testassignments'][1].id,
                    data_dict['testassignments'][2].id
                ])
        qualifying_studentids = collector.get_relatedstudents_that_qualify_for_exam()
        self.assertEqual(qualifying_studentids[0], data_dict['relatedstudent'].id)

    def test_student_qualify_with_all_assignments_qualify_with_custom_score(self):
        data_dict = self._build_data_set(
                grading_plugin=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
                min_points=10,
                max_points=10
        )
        data_dict['testfeedbacksets'][0].grading_points = 5
        data_dict['testfeedbacksets'][1].grading_points = 5
        data_dict['testfeedbacksets'][2].grading_points = 5
        data_dict['testfeedbacksets'][0].save()
        data_dict['testfeedbacksets'][1].save()
        data_dict['testfeedbacksets'][2].save()

        # Set custom score to 10, the student have 15 points.
        collector = resultscollector.PeriodResultSetCollector(
                custom_min_passing_score=10,
                period=data_dict['testperiod'],
                qualifying_assignment_ids=[
                    data_dict['testassignments'][0].id,
                    data_dict['testassignments'][1].id,
                    data_dict['testassignments'][2].id
                ])
        qualifying_studentids = collector.get_relatedstudents_that_qualify_for_exam()
        self.assertEqual(qualifying_studentids[0], data_dict['relatedstudent'].id)

    def test_student_does_not_qualify_with_all_assignments_qualify_without_custom_score(self):
        data_dict = self._build_data_set(
                grading_plugin=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
                min_points=5,
                max_points=5
        )

        collector = resultscollector.PeriodResultSetCollector(
                period=data_dict['testperiod'],
                qualifying_assignment_ids=[
                    data_dict['testassignments'][0].id,
                    data_dict['testassignments'][1].id,
                    data_dict['testassignments'][2].id
                ])
        qualifying_studentids = collector.get_relatedstudents_that_qualify_for_exam()
        self.assertEqual(len(qualifying_studentids), 0)

    def test_student_does_not_qualify_with_all_assignments_qualify_with_custom_score(self):
        data_dict = self._build_data_set(
                grading_plugin=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
                min_points=5,
                max_points=5
        )

        # Set the custom score to 10, the student has 3.
        collector = resultscollector.PeriodResultSetCollector(
                custom_min_passing_score=10,
                period=data_dict['testperiod'],
                qualifying_assignment_ids=[
                    data_dict['testassignments'][0].id,
                    data_dict['testassignments'][1].id,
                    data_dict['testassignments'][2].id
                ])
        qualifying_studentids = collector.get_relatedstudents_that_qualify_for_exam()
        self.assertEqual(len(qualifying_studentids), 0)

    def test_one_student_qualify_with_all_assignments_qualify_without_custom_score(self):
        # Two students are created for the period where only one student have enough points
        # to qualify for the final exam.
        data_dict = self._build_data_set(
                grading_plugin=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
                min_points=5,
                max_points=5
        )

        # Create a new student and to the assignments
        assigngroup1 = baker.make('core.AssignmentGroup', parentnode=data_dict['testassignments'][0])
        assigngroup2 = baker.make('core.AssignmentGroup', parentnode=data_dict['testassignments'][1])
        assigngroup3 = baker.make('core.AssignmentGroup', parentnode=data_dict['testassignments'][2])

        # Create FeedbackSets
        devilry_group_baker_factories.feedbackset_first_attempt_published(group=assigngroup1, grading_points=5)
        devilry_group_baker_factories.feedbackset_first_attempt_published(group=assigngroup2, grading_points=5)
        devilry_group_baker_factories.feedbackset_first_attempt_published(group=assigngroup3, grading_points=5)

        # Create a student with user
        student_user = baker.make(settings.AUTH_USER_MODEL, shortname='dewduc', fullname='Dewey Duck')
        relatedstudent = baker.make('core.RelatedStudent', user=student_user, period=data_dict['testperiod'])

        # Create candidates with relatedstudents and assignmentgroups
        baker.make('core.Candidate', relatedstudent=relatedstudent, assignment_group=assigngroup1)
        baker.make('core.Candidate', relatedstudent=relatedstudent, assignment_group=assigngroup2)
        baker.make('core.Candidate', relatedstudent=relatedstudent, assignment_group=assigngroup3)

        collector = resultscollector.PeriodResultSetCollector(
                period=data_dict['testperiod'],
                qualifying_assignment_ids=[
                    data_dict['testassignments'][0].id,
                    data_dict['testassignments'][1].id,
                    data_dict['testassignments'][2].id
                ])
        qualifying_studentids = collector.get_relatedstudents_that_qualify_for_exam()
        self.assertEqual(len(qualifying_studentids), 1)
        self.assertIn(relatedstudent.id, qualifying_studentids)
        self.assertNotIn(data_dict['relatedstudent'].id, qualifying_studentids)

    def test_one_student_qualify_with_all_assignments_qualify_with_custom_score(self):
        # Two students are created for the period where only one student have enough points
        # to qualify for the final exam.
        data_dict = self._build_data_set(
                grading_plugin=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
                min_points=5,
                max_points=5
        )

        # Create a new student and to the assignments
        assigngroup1 = baker.make('core.AssignmentGroup', parentnode=data_dict['testassignments'][0])
        assigngroup2 = baker.make('core.AssignmentGroup', parentnode=data_dict['testassignments'][1])
        assigngroup3 = baker.make('core.AssignmentGroup', parentnode=data_dict['testassignments'][2])

        # Create FeedbackSets
        devilry_group_baker_factories.feedbackset_first_attempt_published(group=assigngroup1, grading_points=5)
        devilry_group_baker_factories.feedbackset_first_attempt_published(group=assigngroup2, grading_points=5)
        devilry_group_baker_factories.feedbackset_first_attempt_published(group=assigngroup3, grading_points=5)

        # Create a student with user
        student_user = baker.make(settings.AUTH_USER_MODEL, shortname='dewduc', fullname='Dewey Duck')
        relatedstudent_dewey = baker.make('core.RelatedStudent', user=student_user, period=data_dict['testperiod'])

        # Create candidates with relatedstudents and assignmentgroups
        baker.make('core.Candidate', relatedstudent=relatedstudent_dewey, assignment_group=assigngroup1)
        baker.make('core.Candidate', relatedstudent=relatedstudent_dewey, assignment_group=assigngroup2)
        baker.make('core.Candidate', relatedstudent=relatedstudent_dewey, assignment_group=assigngroup3)

        # Set custom score to 10, one student(dewey) has 15 points, and the other student has 3 points
        collector = resultscollector.PeriodResultSetCollector(
                custom_min_passing_score=10,
                period=data_dict['testperiod'],
                qualifying_assignment_ids=[
                    data_dict['testassignments'][0].id,
                    data_dict['testassignments'][1].id,
                    data_dict['testassignments'][2].id
                ])
        qualifying_studentids = collector.get_relatedstudents_that_qualify_for_exam()
        self.assertEqual(len(qualifying_studentids), 1)
        self.assertIn(relatedstudent_dewey.id, qualifying_studentids)
        self.assertNotIn(data_dict['relatedstudent'].id, qualifying_studentids)
