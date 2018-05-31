from django import test
from django.conf import settings
from django.core.files.base import ContentFile
from model_mommy import mommy

from devilry.devilry_comment.models import Comment, CommentEditHistory
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestGroupCommentTriggers(test.TransactionTestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_delete(self):
        testcomment = mommy.make('devilry_comment.Comment')
        testcomment_id = testcomment.id
        testcommentfile = mommy.make('devilry_comment.CommentFile',
                                     comment=testcomment)
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        testcomment.delete()
        self.assertFalse(Comment.objects.filter(id=testcomment_id).exists())


class TestCommentEditTriggers(test.TransactionTestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_not_create_when_comment_is_created(self):
        mommy.make('devilry_comment.Comment', text='Test')
        self.assertEqual(CommentEditHistory.objects.count(), 0)

    def test_comment_history_model_created_on_comment_update(self):
        testcomment = mommy.make('devilry_comment.Comment', text='Test')
        testcomment.save()
        self.assertEqual(CommentEditHistory.objects.count(), 1)

    def test_comment_history_model_created_fields(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        testcomment = mommy.make('devilry_comment.Comment', text='Test', user=user)
        testcomment.text = 'Test edited'
        testcomment.save()
        comment_history = CommentEditHistory.objects.get()
        self.assertEqual(comment_history.comment, testcomment)
        self.assertEqual(comment_history.pre_edit_text, 'Test')
        self.assertEqual(comment_history.post_edit_text, 'Test edited')
        self.assertEqual(comment_history.edited_by, testcomment.user)
