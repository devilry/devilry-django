from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy


class TestFeedbackfeedModel(TestCase):

    def test_clean_published_by_is_none(self):
        feedbackset = mommy.prepare('devilry_group.FeedbackSet',
                                    grading_published_datetime=timezone.now(),
                                    grading_published_by=None,
                                    grading_points=10)
        with self.assertRaisesMessage(ValidationError,
                                      'An assignment can not be published without providing "points".'):
            feedbackset.clean()

    def test_clean_grading_points_is_none(self):
        feedbackset = mommy.prepare('devilry_group.FeedbackSet',
                                    grading_published_datetime=timezone.now(),
                                    grading_published_by=None,
                                    grading_points=10)
        with self.assertRaisesMessage(ValidationError,
                                      'An assignment can not be published without providing "points".'):
            feedbackset.clean()