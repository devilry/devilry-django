from django.core.files.base import ContentFile
from django.test import TestCase
from devilry.apps.core.models import StaticFeedbackFileAttachment
from devilry.devilry_gradingsystem.models import FeedbackDraft, FeedbackDraftFile

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder


class TestFeedbackDraft(TestCase):
    def setUp(self):
        self.testexaminer = UserBuilder('testexaminer').user
        self.assignment1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        self.assignment1builder.update(
            points_to_grade_mapper='raw-points',
            passing_grade_min_points=20,
            max_points=100)
        self.deliverybuilder = self.assignment1builder.add_group(examiners=[self.testexaminer])\
            .add_deadline_in_x_weeks(weeks=1)\
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
        self.assertEquals(staticfeedback.rendered_view, '<p>Test</p>')
        self.assertEquals(staticfeedback.points, 30)
        self.assertEquals(staticfeedback.is_passing_grade, True)


class TestFeedbackDraftFile(TestCase):
    def setUp(self):
        self.testexaminer = UserBuilder('testexaminer').user
        self.assignment1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')
        self.assignment1builder.update(
            points_to_grade_mapper='raw-points',
            passing_grade_min_points=20,
            max_points=100)
        self.deliverybuilder = self.assignment1builder.add_group(examiners=[self.testexaminer])\
            .add_deadline_in_x_weeks(weeks=1)\
            .add_delivery_x_hours_before_deadline(hours=1)

    def test_to_staticfeedbackfileattachment(self):
        draftfile = FeedbackDraftFile(
            delivery=self.deliverybuilder.delivery,
            saved_by=self.testexaminer,
            filename='test.txt')
        draftfile.file.save('test.txt', ContentFile('Test'))
        staticfeedback = self.deliverybuilder.add_passed_A_feedback(saved_by=self.testexaminer).feedback
        fileattachment = draftfile.to_staticfeedbackfileattachment(staticfeedback)
        self.assertEquals(fileattachment.filename, 'test.txt')
        self.assertEquals(fileattachment.file.read(), 'Test')
        self.assertEquals(fileattachment.staticfeedback, staticfeedback)
        self.assertIsNotNone(fileattachment.pk)
        self.assertTrue(StaticFeedbackFileAttachment.objects.filter(pk=fileattachment.pk).exists())
