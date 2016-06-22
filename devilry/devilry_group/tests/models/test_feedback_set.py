from django.core.exceptions import ValidationError
from django.conf import settings

from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from devilry.devilry_group import models as group_models
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy


class TestFeedbackSetModel(TestCase):

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
        self.assertEquals(feedbackset.feedbackset_type, group_models.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT)

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

    def test_feedbackset_current_deadline_first_attempt(self):
        test_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=test_assignment)
        self.assertEquals(test_feedbackset.current_deadline(), test_assignment.first_deadline)

    def test_feedbackset_current_deadline_not_first_attempt(self):
        test_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        test_feedbackset = mommy.make('devilry_group.FeedbackSet',
                                      group__parentnode=test_assignment,
                                      deadline_datetime=timezone.now(),
                                      feedbackset_type=group_models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT)
        self.assertEquals(test_feedbackset.current_deadline(), test_feedbackset.deadline_datetime)
        self.assertNotEquals(test_feedbackset.current_deadline(), test_assignment.first_deadline)

    def test_feedbackset_current_deadline_is_none(self):
        test_assignment = mommy.make('core.Assignment')
        test_feedbackset = mommy.make('devilry_group.FeedbackSet',
                                      group__parentnode=test_assignment)
        self.assertIsNone(test_feedbackset.current_deadline())

    def test_feedback_set_publish(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        grading_points = 10
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
                deadline_datetime=timezone.now() - timezone.timedelta(days=1))
        result, msg = test_feedbackset.publish(published_by=testuser, grading_points=grading_points)
        self.assertTrue(result)
        self.assertEquals(msg, '')
        self.assertIsNotNone(test_feedbackset.grading_published_datetime)
        self.assertEquals(grading_points, test_feedbackset.grading_points)
        self.assertEquals(testuser, test_feedbackset.grading_published_by)

    def test_feedback_set_publish_multiple_feedbackcomments_order(self):
        examiner = mommy.make('core.Examiner')
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(deadline_datetime=timezone.now())
        mommy.make('devilry_group.GroupComment',
                   user_role='examiner',
                   user=examiner.relatedexaminer.user,
                   feedback_set=testfeedbackset,
                   part_of_grading=True,
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   text='comment1')
        mommy.make('devilry_group.GroupComment',
                   user_role='examiner',
                   user=examiner.relatedexaminer.user,
                   feedback_set=testfeedbackset,
                   part_of_grading=True,
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   text='comment2')
        mommy.make('devilry_group.GroupComment',
                   user_role='examiner',
                   user=examiner.relatedexaminer.user,
                   feedback_set=testfeedbackset,
                   part_of_grading=True,
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   text='comment3')
        testfeedbackset.publish(published_by=examiner.relatedexaminer.user, grading_points=1)
        groupcomments = group_models.GroupComment.objects.\
            filter(feedback_set__id=testfeedbackset.id).\
            order_by('published_datetime')
        self.assertEquals(groupcomments[0].text, 'comment1')
        self.assertEquals(groupcomments[1].text, 'comment2')
        self.assertEquals(groupcomments[2].text, 'comment3')

    def test_feedbackset_publish_set_current_deadline_not_expired(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        grading_points = 10
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
                deadline_datetime=timezone.now() + timezone.timedelta(days=1))
        result, msg = test_feedbackset.publish(published_by=testuser, grading_points=grading_points)
        self.assertFalse(result)
        self.assertEquals(msg, 'The deadline has not expired. Feedback was saved, but not published.')

    def test_feedbackset_publish_current_deadline_is_none(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        grading_points = 10
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished()
        result, msg = test_feedbackset.publish(published_by=testuser, grading_points=grading_points)
        self.assertFalse(result)
        self.assertEquals(msg, 'Cannot publish feedback without a deadline.')

    def test_feedbackset_publish_published_by_is_none(self):
        grading_points = 10
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
                deadline_datetime=timezone.now() - timezone.timedelta(days=1))
        with self.assertRaisesMessage(ValidationError,
                                      'An assignment can not be published without being published by someone.'):
            test_feedbackset.publish(published_by=None, grading_points=grading_points)

    def test_feedbackset_publish_grading_points_is_none(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
                deadline_datetime=timezone.now() - timezone.timedelta(days=1))
        with self.assertRaisesMessage(ValidationError,
                                      'An assignment can not be published without providing "points".'):
            result, msg = test_feedbackset.publish(published_by=testuser, grading_points=None)

    def test_feedbackset_clean_is_last_in_group_false(self):
        feedbackset = mommy.prepare('devilry_group.FeedbackSet',
                                    is_last_in_group=False)
        with self.assertRaisesMessage(ValidationError,
                                      'is_last_in_group can not be false.'):
            feedbackset.clean()

    def test_clean_published_by_is_none(self):
        testfeedbackset = mommy.prepare('devilry_group.FeedbackSet',
                                        grading_published_datetime=timezone.now(),
                                        grading_published_by=None,
                                        grading_points=10)
        with self.assertRaisesMessage(ValidationError,
                                      'An assignment can not be published without being published by someone.'):
            testfeedbackset.clean()

    def test_clean_grading_points_is_none(self):
        testuser = mommy.prepare(settings.AUTH_USER_MODEL)
        testfeedbackset = mommy.prepare('devilry_group.FeedbackSet',
                                        grading_published_datetime=timezone.now(),
                                        grading_published_by=testuser,
                                        grading_points=None)
        with self.assertRaisesMessage(ValidationError,
                                      'An assignment can not be published without providing "points".'):
            testfeedbackset.clean()