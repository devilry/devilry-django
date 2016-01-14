from django import test
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

from model_mommy import mommy

from devilry.devilry_group import models as group_models

class TestFeedbackSet(test.TestCase):

    def test_feedbackset_group(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 group=testgroup)
        self.assertEquals(feedbackset.group, testgroup)

    def test_feedbackset_is_last_in_group_default_true(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet')
        self.assertTrue(feedbackset.is_last_in_group)

    def test_feedbackset_feedbackset_type_default_first_try(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet')
        self.assertEquals(feedbackset.feedbackset_type, group_models.FeedbackSet.FEEDBACKSET_TYPE_FIRST_TRY)

    def test_feedbackset_created_by(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        feedbackset = mommy.make('devilry_group.FeedbackSet', created_by=testuser)
        self.assertEquals(feedbackset.created_by, testuser)

    def test_feedbackset_created_datetime(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet')
        self.assertIsNotNone(feedbackset.created_datetime)

    def test_feedbackset_deadline_datetime_default_none(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet')
        self.assertIsNone(feedbackset.deadline_datetime)

    def test_feedbackset_grading_published_datetime_default_none(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet')
        self.assertIsNone(feedbackset.grading_published_datetime)

    def test_feedbackset_grading_published_datetime(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet', grading_published_datetime=timezone.now())
        self.assertIsNotNone(feedbackset.grading_published_datetime)

    def test_feedbackset_grading_published_by_default_none(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet')
        self.assertIsNone(feedbackset.grading_published_by)

    def test_feedbackset_grading_points_default_none(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet')
        self.assertIsNone(feedbackset.grading_points)

    def test_feedbackset_grading_points(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet', grading_points=10)
        self.assertEquals(feedbackset.grading_points, 10)

    def test_feedbackset_clean_grading_published_by_is_none(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet', grading_published_datetime=timezone.now())
        with self.assertRaisesMessage(ValidationError, 'An assignment can not be published '
                                                       'without being published by someone.'):
            feedbackset.clean()

    def test_feedbackset_clean_grading_points_is_none(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 grading_published_datetime=timezone.now(),
                                 grading_published_by=testuser)
        with self.assertRaisesMessage(ValidationError, 'An assignment can not be published '
                                                       'without providing "points"'):
            feedbackset.clean()

    def test_feedbackset_clean_is_last_in_group_false(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet', is_last_in_group=False)
        with self.assertRaisesMessage(ValidationError, 'is_last_in_group can not be false.'):
            feedbackset.clean()

    def test_feedbackset_unicode(self):
        assignment = mommy.make('core.Assignment')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=group)
        cmp_str = u'{} - {} - {}'.format(assignment, group, feedbackset.deadline_datetime)
        self.assertEquals(feedbackset.__unicode__(), cmp_str)
