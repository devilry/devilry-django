import os

from django.core.files.base import ContentFile
from django.test import TestCase
from model_bakery import baker

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group.models import FeedbackSet


class TestFeedbackfeedModel(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_delete_deletes_comment_files(self):
        testfeedbackset = baker.make('devilry_group.FeedbackSet')
        testcomment = baker.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset)
        testcommentfile = baker.make('devilry_comment.CommentFile',
                                     comment=testcomment)
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        filepath = testcommentfile.file.path
        self.assertTrue(os.path.exists(filepath))
        testfeedbackset.delete()
        self.assertFalse(os.path.exists(filepath))

    def test_bulk_delete_deletes_comment_files(self):
        testfeedbackset = baker.make('devilry_group.FeedbackSet')
        testcomment = baker.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset)
        testcommentfile = baker.make('devilry_comment.CommentFile',
                                     comment=testcomment)
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        filepath = testcommentfile.file.path
        self.assertTrue(os.path.exists(filepath))
        FeedbackSet.objects.all().delete()
        self.assertFalse(os.path.exists(filepath))

    def test_bulk_delete_assignmentgroup_deletes_comment_files(self):
        testfeedbackset = baker.make('devilry_group.FeedbackSet')
        testcomment = baker.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset)
        testcommentfile = baker.make('devilry_comment.CommentFile',
                                     comment=testcomment)
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        filepath = testcommentfile.file.path
        self.assertTrue(os.path.exists(filepath))
        AssignmentGroup.objects.all().delete()
        self.assertFalse(os.path.exists(filepath))
