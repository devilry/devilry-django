from django.test import TestCase
from devilry.devilry_gradingsystem.models import FeedbackDraft

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
