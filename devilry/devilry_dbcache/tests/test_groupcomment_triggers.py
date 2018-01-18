from django import test
from django.core.files.base import ContentFile
from model_mommy import mommy

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group.models import GroupComment


class TestGroupCommentTriggers(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_delete(self):
        testcomment = mommy.make('devilry_group.GroupComment')
        testcomment_id = testcomment.id
        testcommentfile = mommy.make('devilry_comment.CommentFile',
                                     comment=testcomment)
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        testcomment.delete()
        self.assertFalse(GroupComment.objects.filter(id=testcomment_id).exists())
