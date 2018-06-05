# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import test
from django.conf import settings
from django.core.files.base import ContentFile
from model_mommy import mommy

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_comment.models import Comment, CommentEditHistory
from devilry.devilry_group.models import GroupComment, GroupCommentEditHistory


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


class TestGroupCommentEditTrigger(test.TransactionTestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_group_comment_edit_history_not_created_on_create_sanity(self):
        mommy.make('devilry_group.GroupComment')
        self.assertEqual(GroupCommentEditHistory.objects.count(), 0)
        self.assertEqual(CommentEditHistory.objects.count(), 0)

    def test_group_comment_edit_history_created_on_update_sanity(self):
        group_comment = mommy.make('devilry_group.GroupComment')
        group_comment.save()
        self.assertEqual(GroupCommentEditHistory.objects.count(), 1)
        self.assertEqual(CommentEditHistory.objects.count(), 1)

    def test_updated_fields(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        group_comment = mommy.make('devilry_group.GroupComment',
                                   text='Comment text', user=user)
        group_comment.text = 'Comment text edited'
        group_comment.save()
        self.assertEqual(GroupCommentEditHistory.objects.count(), 1)
        self.assertEqual(CommentEditHistory.objects.count(), 1)
        group_comment_edit_history = GroupCommentEditHistory.objects.get()
        self.assertEqual(group_comment_edit_history.group_comment, group_comment)
        self.assertEqual(group_comment_edit_history.pre_edit_text, 'Comment text')
        self.assertEqual(group_comment_edit_history.post_edit_text, 'Comment text edited')
        self.assertEqual(group_comment_edit_history.edited_by, user)

    def test_group_comment_history_comment_history_no_duplicates(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        group_comment = mommy.make('devilry_group.GroupComment',
                                   text='Comment text 1', user=user)
        group_comment.text = 'Comment text 2'
        group_comment.save()
        self.assertEqual(GroupCommentEditHistory.objects.count(), 1)
        self.assertEqual(CommentEditHistory.objects.count(), 1)

    def test_group_comment_history_points_to_comment_history(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        group_comment = mommy.make('devilry_group.GroupComment',
                                   text='Comment text 1', user=user)
        group_comment.text = 'Comment text 2'
        group_comment.save()
        self.assertEqual(GroupCommentEditHistory.objects.count(), 1)
        self.assertEqual(CommentEditHistory.objects.count(), 1)
        groupcommentedit_history = GroupCommentEditHistory.objects.get()
        commentedit_history = CommentEditHistory.objects.get()
        self.assertEqual(groupcommentedit_history.id, commentedit_history.id)
        self.assertEqual(groupcommentedit_history.commentedithistory_ptr_id, commentedit_history.id)
        self.assertEqual(groupcommentedit_history.commentedithistory_ptr, commentedit_history)

    def test_multiple_updates(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        group_comment = mommy.make('devilry_group.GroupComment',
                                   text='Comment text 1', user=user)
        group_comment.text = 'Comment text 2'
        group_comment.save()
        group_comment.text = 'Comment text 3'
        group_comment.save()
        self.assertEqual(GroupCommentEditHistory.objects.count(), 2)
        self.assertEqual(CommentEditHistory.objects.count(), 2)
        groupcommentedit_history = GroupCommentEditHistory.objects.order_by('edited_datetime')
        commentedit_history = CommentEditHistory.objects.order_by('edited_datetime')
        self.assertEqual(groupcommentedit_history[0].commentedithistory_ptr_id, commentedit_history[0].id)
        self.assertEqual(groupcommentedit_history[1].commentedithistory_ptr_id, commentedit_history[1].id)

        # Test for CommentEditHistory entries
        self.assertEqual(commentedit_history[0].pre_edit_text, 'Comment text 1')
        self.assertEqual(commentedit_history[0].post_edit_text, 'Comment text 2')
        self.assertEqual(commentedit_history[1].pre_edit_text, 'Comment text 2')
        self.assertEqual(commentedit_history[1].post_edit_text, 'Comment text 3')

        # Test for GroupCommentEditHistory entries. This is basically the same as the checks above
        # but Django makes it seem as GroupCommentEditHistory has the fields pre_edit_text and post_edit_text
        # when Django actually joins the table of the superclass and does a fk related lookup.
        self.assertEqual(groupcommentedit_history[0].pre_edit_text, 'Comment text 1')
        self.assertEqual(groupcommentedit_history[0].post_edit_text, 'Comment text 2')
        self.assertEqual(groupcommentedit_history[1].pre_edit_text, 'Comment text 2')
        self.assertEqual(groupcommentedit_history[1].post_edit_text, 'Comment text 3')
