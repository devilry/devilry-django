from django import test
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.db import InternalError
from model_bakery import baker

from devilry.devilry_comment.models import Comment, CommentEditHistory
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestGroupCommentTriggers(test.TestCase):
    def setUp(self):
        ContentType.objects.clear_cache()
        AssignmentGroupDbCacheCustomSql().initialize()

    def tearDown(self):
        ContentType.objects.clear_cache()

    def test_delete(self):
        testcomment = baker.make('devilry_comment.Comment')
        testcomment_id = testcomment.id
        testcommentfile = baker.make('devilry_comment.CommentFile',
                                     comment=testcomment)
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        testcomment.delete()
        self.assertFalse(Comment.objects.filter(id=testcomment_id).exists())


class TestCommentEditTriggers(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_id_update_raise_internal_error(self):
        comment = baker.make('devilry_comment.Comment', text='Test')
        with self.assertRaises(InternalError):
            Comment.objects.filter(id=comment.id).update(id=2)

    def test_not_create_when_comment_is_created(self):
        baker.make('devilry_comment.Comment', text='Test')
        self.assertEqual(CommentEditHistory.objects.count(), 0)

    def test_comment_history_model_created_on_comment_update(self):
        testcomment = baker.make('devilry_comment.Comment', text='Test')
        testcomment.save()
        self.assertEqual(CommentEditHistory.objects.count(), 1)

    def test_comment_history_model_created_fields(self):
        user = baker.make(settings.AUTH_USER_MODEL)
        testcomment = baker.make('devilry_comment.Comment', text='Test', user=user)
        testcomment.text = 'Test edited'
        testcomment.save()
        comment_history = CommentEditHistory.objects.get()
        self.assertEqual(comment_history.comment, testcomment)
        self.assertEqual(comment_history.pre_edit_text, 'Test')
        self.assertEqual(comment_history.post_edit_text, 'Test edited')
        self.assertEqual(comment_history.edited_by, testcomment.user)
