import os

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.conf import settings

from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.models import FeedbackSet


class TestFeedbackfeedModel(TestCase):

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
        self.assertEquals(feedbackset.feedbackset_type, FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT)

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

    def test_delete_deletes_comment_files(self):
        testfeedbackset = mommy.make('devilry_group.FeedbackSet')
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset)
        testcommentfile = mommy.make('devilry_comment.CommentFile',
                                     comment=testcomment)
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        filepath = testcommentfile.file.path
        self.assertTrue(os.path.exists(filepath))
        testfeedbackset.delete()
        self.assertFalse(os.path.exists(filepath))

    def test_bulk_delete_deletes_comment_files(self):
        testfeedbackset = mommy.make('devilry_group.FeedbackSet')
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset)
        testcommentfile = mommy.make('devilry_comment.CommentFile',
                                     comment=testcomment)
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        filepath = testcommentfile.file.path
        self.assertTrue(os.path.exists(filepath))
        FeedbackSet.objects.all().delete()
        self.assertFalse(os.path.exists(filepath))

    def test_bulk_delete_assignmentgroup_deletes_comment_files(self):
        testfeedbackset = mommy.make('devilry_group.FeedbackSet')
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset)
        testcommentfile = mommy.make('devilry_comment.CommentFile',
                                     comment=testcomment)
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        filepath = testcommentfile.file.path
        self.assertTrue(os.path.exists(filepath))
        AssignmentGroup.objects.all().delete()
        self.assertFalse(os.path.exists(filepath))
