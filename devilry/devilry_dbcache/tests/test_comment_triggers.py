from django import test
from django.core.files.base import ContentFile
from model_mommy import mommy

from devilry.devilry_comment.models import Comment
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
