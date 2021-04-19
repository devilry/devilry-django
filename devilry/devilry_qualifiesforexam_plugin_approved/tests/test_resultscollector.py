# -*- coding: utf-8 -*-


# Django imports
from django import test

# Devilry imports
from model_bakery import baker
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.project.common import settings
from devilry.devilry_group import devilry_group_baker_factories
from devilry.devilry_qualifiesforexam.tests import test_pluginhelpers
from devilry.devilry_qualifiesforexam_plugin_approved import resultscollector


class TestPeriodResultSetCollector(test.TestCase, test_pluginhelpers.TestPluginHelper):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_student_pass_with_all_assignments_qualify(self):
        data_dict = self._build_data_set()
        collector = resultscollector.PeriodResultSetCollector(period=data_dict['testperiod'])
        qualifying_studentids = collector.get_relatedstudents_that_qualify_for_exam()
        self.assertEqual(len(qualifying_studentids), 1)
        self.assertEqual(qualifying_studentids[0], data_dict['relatedstudent'].id)

    def test_student_fails_with_all_assignments_qualify(self):
        data_dict = self._build_data_set()
        data_dict['testfeedbacksets'][0].grading_points = 0
        data_dict['testfeedbacksets'][0].save()
        collector = resultscollector.PeriodResultSetCollector(period=data_dict['testperiod'])
        qualifying_studentids = collector.get_relatedstudents_that_qualify_for_exam()
        self.assertEqual(len(qualifying_studentids), 0)

    def test_student_pass_with_subset_of_assignments_qualify(self):
        data_dict = self._build_data_set()
        collector = resultscollector.PeriodResultSetCollector(
            period=data_dict['testperiod'],
            qualifying_assignment_ids=[
                data_dict['testassignments'][0].id,
                data_dict['testassignments'][1].id,
            ]
        )
        qualifying_studentids = collector.get_relatedstudents_that_qualify_for_exam()
        self.assertEqual(len(qualifying_studentids), 1)
        self.assertEqual(qualifying_studentids[0], data_dict['relatedstudent'].id)

    def test_student_fails_with_subset_of_assignments_qualify(self):
        data_dict = self._build_data_set()
        data_dict['testfeedbacksets'][1].grading_points = 0
        data_dict['testfeedbacksets'][1].save()
        collector = resultscollector.PeriodResultSetCollector(
            period=data_dict['testperiod'],
            qualifying_assignment_ids=[
                data_dict['testassignments'][0].id,
                data_dict['testassignments'][1].id,
            ]
        )
        qualifying_studentids = collector.get_relatedstudents_that_qualify_for_exam()
        self.assertEqual(len(qualifying_studentids), 0)

    def test_student_pass_with_one_failed_assignment_not_qualifying(self):
        data_dict = self._build_data_set()

        # set FeedbackSet.grading_points on the Assignment that's NOT qualifying
        data_dict['testfeedbacksets'][2].grading_points = 0
        data_dict['testfeedbacksets'][2].save()
        collector = resultscollector.PeriodResultSetCollector(
            period=data_dict['testperiod'],
            qualifying_assignment_ids=[
                data_dict['testassignments'][0].id,
                data_dict['testassignments'][1].id,
            ]
        )
        qualifying_studentids = collector.get_relatedstudents_that_qualify_for_exam()
        self.assertEqual(len(qualifying_studentids), 1)
        self.assertEqual(qualifying_studentids[0], data_dict['relatedstudent'].id)

    def test_all_students_pass_with_all_assignments_qualify(self):
        data_dict = self._build_data_set()

        # Create a new student and to the assignments
        assigngroup1 = baker.make('core.AssignmentGroup', parentnode=data_dict['testassignments'][0])
        assigngroup2 = baker.make('core.AssignmentGroup', parentnode=data_dict['testassignments'][1])
        assigngroup3 = baker.make('core.AssignmentGroup', parentnode=data_dict['testassignments'][2])

        # Create FeedbackSets
        devilry_group_baker_factories.feedbackset_first_attempt_published(group=assigngroup1, grading_points=1)
        devilry_group_baker_factories.feedbackset_first_attempt_published(group=assigngroup2, grading_points=1)
        devilry_group_baker_factories.feedbackset_first_attempt_published(group=assigngroup3, grading_points=1)

        # Create a student with user
        student_user = baker.make(settings.AUTH_USER_MODEL, shortname='dewduc', fullname='Dewey Duck')
        relatedstudent = baker.make('core.RelatedStudent', user=student_user, period=data_dict['testperiod'])

        # Create candidates with relatedstudents and assignmentgroups
        baker.make('core.Candidate', relatedstudent=relatedstudent, assignment_group=assigngroup1)
        baker.make('core.Candidate', relatedstudent=relatedstudent, assignment_group=assigngroup2)
        baker.make('core.Candidate', relatedstudent=relatedstudent, assignment_group=assigngroup3)

        collector = resultscollector.PeriodResultSetCollector(period=data_dict['testperiod'])
        qualifying_studentids = collector.get_relatedstudents_that_qualify_for_exam()
        self.assertEqual(len(qualifying_studentids), 2)
        self.assertTrue(relatedstudent.id in qualifying_studentids)
        self.assertTrue(data_dict['relatedstudent'].id in qualifying_studentids)

    def test_one_students_pass_with_all_assignments_qualify(self):
        data_dict = self._build_data_set()

        # Create a new student and to the assignments
        assigngroup1 = baker.make('core.AssignmentGroup', parentnode=data_dict['testassignments'][0])
        assigngroup2 = baker.make('core.AssignmentGroup', parentnode=data_dict['testassignments'][1])
        assigngroup3 = baker.make('core.AssignmentGroup', parentnode=data_dict['testassignments'][2])

        # Create FeedbackSets for student, with one FeedbackSet with a score of 0. Since all Assignments qualifies,
        # this student should not qualify for final exam.
        devilry_group_baker_factories.feedbackset_first_attempt_published(group=assigngroup1, grading_points=0)
        devilry_group_baker_factories.feedbackset_first_attempt_published(group=assigngroup2, grading_points=1)
        devilry_group_baker_factories.feedbackset_first_attempt_published(group=assigngroup3, grading_points=1)

        # Create a student with user
        student_user = baker.make(settings.AUTH_USER_MODEL, shortname='dewduc', fullname='Dewey Duck')
        relatedstudent = baker.make('core.RelatedStudent', user=student_user, period=data_dict['testperiod'])

        # Create candidates with relatedstudents and assignmentgroups
        baker.make('core.Candidate', relatedstudent=relatedstudent, assignment_group=assigngroup1)
        baker.make('core.Candidate', relatedstudent=relatedstudent, assignment_group=assigngroup2)
        baker.make('core.Candidate', relatedstudent=relatedstudent, assignment_group=assigngroup3)

        collector = resultscollector.PeriodResultSetCollector(period=data_dict['testperiod'])
        qualifying_studentids = collector.get_relatedstudents_that_qualify_for_exam()
        self.assertEqual(len(qualifying_studentids), 1)
        self.assertTrue(relatedstudent.id not in qualifying_studentids)
        self.assertTrue(data_dict['relatedstudent'].id in qualifying_studentids)
