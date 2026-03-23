# -*- coding: utf-8 -*-


# Django imports
from django import test
from django.conf import settings
from model_bakery import baker

# Devilry imports
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_qualifiesforexam.tests import test_pluginhelpers
from devilry.devilry_qualifiesforexam_plugin_students import resultscollector


class TestPeriodResultSetCollector(test.TestCase, test_pluginhelpers.TestPluginHelper):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        self.period = baker.make_recipe("devilry.apps.core.period_active")
        self.assignment = baker.make("core.Assignment", parentnode=self.period, passing_grade_min_points=50, max_points=100)
        self.student_user1 = baker.make(settings.AUTH_USER_MODEL, shortname="student1", fullname="Student One")
        self.student_user2 = baker.make(settings.AUTH_USER_MODEL, shortname="student2", fullname="Student Two")
        self.student_user3 = baker.make(settings.AUTH_USER_MODEL, shortname="student3", fullname="Student Three")
        self.relatedstudent1 = baker.make("core.RelatedStudent", user=self.student_user1, period=self.period)
        self.relatedstudent2 = baker.make("core.RelatedStudent", user=self.student_user2, period=self.period)
        self.relatedstudent3 = baker.make("core.RelatedStudent", user=self.student_user3, period=self.period)
        self.assignmentgroup1 = baker.make("core.AssignmentGroup", parentnode=self.assignment)
        self.assignmentgroup2 = baker.make("core.AssignmentGroup", parentnode=self.assignment)
        self.assignmentgroup3 = baker.make("core.AssignmentGroup", parentnode=self.assignment)
        baker.make("core.Candidate", relatedstudent=self.relatedstudent1, assignment_group=self.assignmentgroup1)
        baker.make("core.Candidate", relatedstudent=self.relatedstudent2, assignment_group=self.assignmentgroup2)
        baker.make("core.Candidate", relatedstudent=self.relatedstudent3, assignment_group=self.assignmentgroup3)
        feedbackset1 = FeedbackSet.objects.get(group=self.assignmentgroup1)
        feedbackset2 = FeedbackSet.objects.get(group=self.assignmentgroup2)
        feedbackset3 = FeedbackSet.objects.get(group=self.assignmentgroup3)
        feedbackset1.grading_points = 30    # Fail
        feedbackset2.grading_points = 70    # Pass
        feedbackset3.grading_points = 100   # Pass
        feedbackset1.save()
        feedbackset2.save()
        feedbackset3.save()

    def test_no_relatedstudent_ids_selected(self):
        collector = resultscollector.PeriodResultSetCollector(
            period=self.period, qualifying_student_ids=[]
        )
        self.assertEqual(collector.get_relatedstudents_that_qualify_for_exam(), [])

    def test_selected_student_qualifies_regardless_of_grading_points(self):
        collector = resultscollector.PeriodResultSetCollector(
            period=self.period, qualifying_student_ids=[self.relatedstudent1.id]
        )
        self.assertEqual(collector.get_relatedstudents_that_qualify_for_exam(), [self.relatedstudent1.id])

    def test_relatedstudent_ids_partial_selected(self):
        collector = resultscollector.PeriodResultSetCollector(
            period=self.period, qualifying_student_ids=[self.relatedstudent1.id, self.relatedstudent2.id]
        )
        self.assertEqual(collector.get_relatedstudents_that_qualify_for_exam(), [self.relatedstudent1.id, self.relatedstudent2.id])

    def test_relatedstudent_ids_all_selected(self):
        collector = resultscollector.PeriodResultSetCollector(
            period=self.period, qualifying_student_ids=[self.relatedstudent1.id, self.relatedstudent2.id, self.relatedstudent3.id,]
        )
        self.assertEqual(collector.get_relatedstudents_that_qualify_for_exam(), [self.relatedstudent1.id, self.relatedstudent2.id, self.relatedstudent3.id])
