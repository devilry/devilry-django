import os

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.models import FeedbackSet


class TestFeedbackfeedModel(TestCase):

    def test_clean_published_by_is_none(self):
        testfeedbackset = mommy.prepare('devilry_group.FeedbackSet',
                                        grading_published_datetime=timezone.now(),
                                        grading_published_by=None,
                                        grading_points=10)
        with self.assertRaisesMessage(ValidationError,
                                      'An assignment can not be published without providing "points".'):
            testfeedbackset.clean()

    def test_clean_grading_points_is_none(self):
        testfeedbackset = mommy.prepare('devilry_group.FeedbackSet',
                                        grading_published_datetime=timezone.now(),
                                        grading_published_by=None,
                                        grading_points=10)
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
