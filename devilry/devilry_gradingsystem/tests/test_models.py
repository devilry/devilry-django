import unittest
from django.core.files.base import ContentFile
from django.test import TestCase
from devilry.apps.core.models import StaticFeedbackFileAttachment
from devilry.devilry_gradingsystem.models import FeedbackDraft, FeedbackDraftFile

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder


@unittest.skip('devilry_gradingsystem will most likely be replaced in 3.0')
class TestFeedbackDraft(TestCase):
    def setUp(self):
        self.testexaminer = UserBuilder('testexaminer').user
        self.assignment1builder = PeriodBuilder.quickadd_ducku_duck1010_active() \
            .add_assignment('assignment1')
        self.assignment1builder.update(
            points_to_grade_mapper='raw-points',
            passing_grade_min_points=20,
            max_points=100)
        self.groupbuilder = self.assignment1builder.add_group(examiners=[self.testexaminer])
        self.deliverybuilder = self.groupbuilder \
            .add_deadline_in_x_weeks(weeks=1) \
            .add_delivery_x_hours_before_deadline(hours=1)

    def test_to_staticfeedback(self):
        feedbackdraft = FeedbackDraft.objects.create(
            delivery=self.deliverybuilder.delivery,
            feedbacktext_raw='Test',
            feedbacktext_html='<p>Test</p>',
            points=30,
            saved_by=self.testexaminer,
            published=True)
        staticfeedback = feedbackdraft.to_staticfeedback()
        self.assertEqual(staticfeedback.rendered_view, '<p>Test</p>')
        self.assertEqual(staticfeedback.points, 30)
        self.assertEqual(staticfeedback.is_passing_grade, True)

    def test_get_last_feedbackdraft_none(self):
        self.assertEqual(
            FeedbackDraft.get_last_feedbackdraft(assignment=self.assignment1builder.assignment,
                                                 delivery=self.deliverybuilder.delivery,
                                                 user=self.testexaminer),
            None)

    def test_get_last_feedbackdraft_feedback_workflow_allows_shared_feedback_drafts(self):
        self.assignment1builder.update(feedback_workflow='trusted-cooperative-feedback-editing')
        feedbackdraft = FeedbackDraft.objects.create(
            delivery=self.deliverybuilder.delivery,
            feedbacktext_raw='Test',
            feedbacktext_html='<p>Test</p>',
            points=30,
            saved_by=UserBuilder('otheruser').user)
        self.assertEqual(
            FeedbackDraft.get_last_feedbackdraft(assignment=self.assignment1builder.assignment,
                                                 delivery=self.deliverybuilder.delivery,
                                                 user=self.testexaminer),
            feedbackdraft)

    def test_get_last_feedbackdraft_feedback_workflow_does_not_allow_shared_feedback_drafts(self):
        FeedbackDraft.objects.create(
            delivery=self.deliverybuilder.delivery,
            feedbacktext_raw='Test',
            feedbacktext_html='<p>Test</p>',
            points=30,
            saved_by=UserBuilder('otheruser').user)
        self.assertEqual(
            FeedbackDraft.get_last_feedbackdraft(assignment=self.assignment1builder.assignment,
                                                 delivery=self.deliverybuilder.delivery,
                                                 user=self.testexaminer),
            None)

    def test_get_last_feedbackdraft_owned(self):
        feedbackdraft = FeedbackDraft.objects.create(
            delivery=self.deliverybuilder.delivery,
            feedbacktext_raw='Test',
            feedbacktext_html='<p>Test</p>',
            points=30,
            saved_by=self.testexaminer)
        self.assertEqual(
            FeedbackDraft.get_last_feedbackdraft(assignment=self.assignment1builder.assignment,
                                                 delivery=self.deliverybuilder.delivery,
                                                 user=self.testexaminer),
            feedbackdraft)

    def test_get_last_feedbackdraft_for_group_none(self):
        self.assertEqual(
            FeedbackDraft.get_last_feedbackdraft_for_group(assignment=self.assignment1builder.assignment,
                                                           group=self.groupbuilder.group,
                                                           user=self.testexaminer),
            None)

    def test_get_last_feedbackdraft_for_group_feedback_workflow_allows_shared_feedback_drafts(self):
        self.assignment1builder.update(feedback_workflow='trusted-cooperative-feedback-editing')
        feedbackdraft = FeedbackDraft.objects.create(
            delivery=self.deliverybuilder.delivery,
            feedbacktext_raw='Test',
            feedbacktext_html='<p>Test</p>',
            points=30,
            saved_by=UserBuilder('otheruser').user)
        self.assertEqual(
            FeedbackDraft.get_last_feedbackdraft_for_group(assignment=self.assignment1builder.assignment,
                                                           group=self.groupbuilder.group,
                                                           user=self.testexaminer),
            feedbackdraft)

    def test_get_last_feedbackdraft_for_group_feedback_workflow_does_not_allow_shared_feedback_drafts(self):
        FeedbackDraft.objects.create(
            delivery=self.deliverybuilder.delivery,
            feedbacktext_raw='Test',
            feedbacktext_html='<p>Test</p>',
            points=30,
            saved_by=UserBuilder('otheruser').user)
        self.assertEqual(
            FeedbackDraft.get_last_feedbackdraft_for_group(assignment=self.assignment1builder.assignment,
                                                           group=self.groupbuilder.group,
                                                           user=self.testexaminer),
            None)

    def test_get_last_feedbackdraft_for_group_owned(self):
        feedbackdraft = FeedbackDraft.objects.create(
            delivery=self.deliverybuilder.delivery,
            feedbacktext_raw='Test',
            feedbacktext_html='<p>Test</p>',
            points=30,
            saved_by=self.testexaminer)
        self.assertEqual(
            FeedbackDraft.get_last_feedbackdraft_for_group(assignment=self.assignment1builder.assignment,
                                                           group=self.groupbuilder.group,
                                                           user=self.testexaminer),
            feedbackdraft)


@unittest.skip('devilry_gradingsystem will most likely be replaced in 3.0')
class TestFeedbackDraftFile(TestCase):
    def setUp(self):
        self.testexaminer = UserBuilder('testexaminer').user
        self.assignment1builder = PeriodBuilder.quickadd_ducku_duck1010_active() \
            .add_assignment('assignment1')
        self.assignment1builder.update(
            points_to_grade_mapper='raw-points',
            passing_grade_min_points=20,
            max_points=100)
        self.deliverybuilder = self.assignment1builder.add_group(examiners=[self.testexaminer]) \
            .add_deadline_in_x_weeks(weeks=1) \
            .add_delivery_x_hours_before_deadline(hours=1)

    def test_to_staticfeedbackfileattachment(self):
        draftfile = FeedbackDraftFile(
            delivery=self.deliverybuilder.delivery,
            saved_by=self.testexaminer,
            filename='test.txt')
        draftfile.file.save('test.txt', ContentFile('Test'))
        staticfeedback = self.deliverybuilder.add_passed_A_feedback(saved_by=self.testexaminer).feedback
        fileattachment = draftfile.to_staticfeedbackfileattachment(staticfeedback)
        self.assertEqual(fileattachment.filename, 'test.txt')
        self.assertEqual(fileattachment.file.read(), 'Test')
        self.assertEqual(fileattachment.staticfeedback, staticfeedback)
        self.assertIsNotNone(fileattachment.pk)
        self.assertTrue(StaticFeedbackFileAttachment.objects.filter(pk=fileattachment.pk).exists())

    def test_get_last_feedbackdraft_feedback_workflow_allows_shared_feedback_drafts(self):
        self.assignment1builder.update(feedback_workflow='trusted-cooperative-feedback-editing')
        feedbackdraft = FeedbackDraftFile.objects.create(
            delivery=self.deliverybuilder.delivery,
            saved_by=UserBuilder('otheruser').user,
            filename='test.txt')
        self.assertEqual(
            FeedbackDraftFile.objects.filter_accessible_files(assignment=self.assignment1builder.assignment,
                                                              delivery=self.deliverybuilder.delivery,
                                                              user=self.testexaminer).first(),
            feedbackdraft)

    def test_get_last_feedbackdraft_feedback_workflow_does_not_allow_shared_feedback_drafts(self):
        FeedbackDraftFile.objects.create(
            delivery=self.deliverybuilder.delivery,
            saved_by=UserBuilder('otheruser').user,
            filename='test.txt')
        self.assertEqual(
            FeedbackDraftFile.objects.filter_accessible_files(assignment=self.assignment1builder.assignment,
                                                              delivery=self.deliverybuilder.delivery,
                                                              user=self.testexaminer).first(),
            None)

    def test_get_last_feedbackdraft_owned(self):
        feedbackdraft = FeedbackDraftFile.objects.create(
            delivery=self.deliverybuilder.delivery,
            saved_by=self.testexaminer,
            filename='test.txt')
        self.assertEqual(
            FeedbackDraftFile.objects.filter_accessible_files(assignment=self.assignment1builder.assignment,
                                                              delivery=self.deliverybuilder.delivery,
                                                              user=self.testexaminer).first(),
            feedbackdraft)
