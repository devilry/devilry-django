# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pprint import pprint

import os
from django.core import files
from django.forms import model_to_dict

from devilry.devilry_merge_v3database.utils import merger
from devilry.apps.core import models as core_models
from devilry.devilry_group import models as group_models
from devilry.devilry_comment import models as comment_models
from devilry.devilry_merge_v3database.models import TempMergeId


class CommentMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.devilry_comment.models.Comment` from database to current default database.
    """
    model = comment_models.Comment

    def select_related_foreign_keys(self):
        return ['user', 'parent']

    def start_migration(self, from_db_object):
        # TODO: Handle parent comments
        user = self.get_user_by_shortname(shortname=from_db_object.user.shortname)
        comment_kwargs = model_to_dict(from_db_object, exclude=[
            'id', 'pk', 'user', 'comment_ptr', 'comment_ptr_id', 'parent'])
        comment = comment_models.Comment(**comment_kwargs)
        if user:
            comment.user_id = user.id
        migrated_comment = self.save_object(obj=comment)

        # Create merge object from Comment
        TempMergeId.objects.create_from_instances(
            merge_to_obj=migrated_comment,
            merge_from_obj=from_db_object
        )


class CommentFileMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.devilry_comment.models.CommentFile` from database to
    current default database.
    """
    model = comment_models.CommentFile

    def __init__(self, migrate_media_root, *args, **kwargs):
        self.migrate_media_root = migrate_media_root
        super(CommentFileMerger, self).__init__(*args, **kwargs)

    def select_related_foreign_keys(self):
        return ['comment']

    def __get_comment_from_temp_merge_id(self, from_db_obj):
        temp_merge_id = TempMergeId.objects.get_from_label_and_merge_from_obj_id(
            model_name='devilry_comment_comment',
            from_id=from_db_obj.comment_id
        )
        try:
            return comment_models.Comment.objects.get(id=temp_merge_id.to_id)
        except comment_models.Comment.DoesNotExist:
            return None

    def start_migration(self, from_db_object):
        comment = self.__get_comment_from_temp_merge_id(from_db_obj=from_db_object)
        if comment:
            comment_file_kwargs = model_to_dict(from_db_object, exclude=['id', 'pk', 'comment', 'file'])
            comment_file = comment_models.CommentFile(**comment_file_kwargs)
            comment_file.comment_id = comment.id
            saved_comment_file = self.save_object(obj=comment_file)
            filepath = os.path.join(self.migrate_media_root, from_db_object.file.name)
            with open(filepath, 'rb') as fp:
                comment_file.file = files.File(fp, saved_comment_file.filename)
                self.save_object(obj=saved_comment_file)
        else:
            raise ValueError('Comments must be imported before CommentFiles.')


class CommentEditHistoryMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.devilry_comment.models.Comment` from database to current default database.
    """
    model = comment_models.CommentEditHistory

    def select_related_foreign_keys(self):
        return ['comment', 'edited_by']

    def __get_edited_by_user(self, comment_edit_history):
        if comment_edit_history.edited_by:
            return self.get_user_by_shortname(shortname=comment_edit_history.edited_by.shortname).id
        return None

    def __get_comment_from_temp_merge_id(self, from_db_obj):
        temp_merge_id = TempMergeId.objects.get_from_label_and_merge_from_obj_id(
            model_name='devilry_comment_comment',
            from_id=from_db_obj.comment_id
        )
        try:
            return comment_models.Comment.objects.get(id=temp_merge_id.to_id)
        except comment_models.Comment.DoesNotExist:
            return None

    def start_migration(self, from_db_object):
        comment = self.__get_comment_from_temp_merge_id(from_db_obj=from_db_object)
        if comment:
            user = self.get_user_by_shortname(shortname=from_db_object.edited_by.shortname)
            comment_edit_history_kwargs = model_to_dict(from_db_object, exclude=[
                'id', 'pk', 'comment', 'edited_by'])
            comment_edit_history = comment_models.CommentEditHistory(**comment_edit_history_kwargs)
            comment_edit_history.comment_id = comment.id
            if user:
                comment_edit_history.edited_by_id = user.id
            migrated_comment_edit_history = self.save_object(obj=comment_edit_history)

            # Create merge object from CommentEditHistory
            TempMergeId.objects.create_from_instances(
                merge_to_obj=migrated_comment_edit_history,
                merge_from_obj=from_db_object
            )
        else:
            raise ValueError('Comments must be imported before CommentEditHistory')


class GroupCommentMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.devilry_group.models.GroupComment` from database to current default database.
    """
    model = group_models.GroupComment

    def select_related_foreign_keys(self):
        return ['feedback_set']

    def __get_feedback_set_from_temp_merge_id(self, from_db_obj):
        temp_merge_id = TempMergeId.objects.get_from_label_and_merge_from_obj_id(
            model_name='devilry_group_feedbackset',
            from_id=from_db_obj.feedback_set_id
        )
        try:
            return group_models.FeedbackSet.objects.get(id=temp_merge_id.to_id)
        except group_models.FeedbackSet.DoesNotExist:
            return None

    def __get_comment_from_temp_merge_id(self, from_db_obj):
        temp_merge_id = TempMergeId.objects.get_from_label_and_merge_from_obj_id(
            model_name='devilry_comment_comment',
            from_id=from_db_obj.comment_ptr_id
        )
        try:
            return comment_models.Comment.objects.get(id=temp_merge_id.to_id)
        except comment_models.Comment.DoesNotExist:
            return None

    def start_migration(self, from_db_object):
        comment = self.__get_comment_from_temp_merge_id(from_db_obj=from_db_object)
        feedback_set = self.__get_feedback_set_from_temp_merge_id(from_db_obj=from_db_object)
        if comment and feedback_set:
            group_comment_kwargs = model_to_dict(from_db_object, exclude=[
                'id', 'pk', 'user', 'comment_ptr', 'comment_ptr_id', 'feedback_set'])
            group_comment = group_models.GroupComment(**group_comment_kwargs)
            group_comment.comment_ptr_id = comment.id
            group_comment.feedback_set_id = feedback_set.id
            group_comment.user_id = comment.user_id
            migrated_group_comment = self.save_object(obj=group_comment)

            # Create merge object from GroupComment
            TempMergeId.objects.create_from_instances(
                merge_to_obj=migrated_group_comment,
                merge_from_obj=from_db_object
            )
        else:
            raise ValueError('FeedbackSets and Comments must be imported before GroupComments.')


class GroupCommentEditHistoryMerger(merger.AbstractMerger):
    """
    Merge :class:`devilry.devilry_group.models.GroupCommentEditHistory` from database to current default database.
    """
    model = group_models.GroupCommentEditHistory

    def select_related_foreign_keys(self):
        return ['commentedithistory_ptr', 'group_comment']

    def __get_comment_from_temp_merge_id(self, from_db_obj):
        temp_merge_id = TempMergeId.objects.get_from_label_and_merge_from_obj_id(
            model_name='devilry_comment_comment',
            from_id=from_db_obj.group_comment_id
        )
        try:
            return comment_models.Comment.objects.get(id=temp_merge_id.to_id)
        except comment_models.Comment.DoesNotExist:
            return None

    def __get_commentedithistory_from_temp_merge_id(self, from_db_obj):
        temp_merge_id = TempMergeId.objects.get_from_label_and_merge_from_obj_id(
            model_name='devilry_comment_comment',
            from_id=from_db_obj.commentedithistory_ptr_id
        )
        try:
            return comment_models.CommentEditHistory.objects.get(id=temp_merge_id.to_id)
        except comment_models.CommentEditHistory.DoesNotExist:
            return None

    def start_migration(self, from_db_object):
        comment = self.__get_comment_from_temp_merge_id(from_db_obj=from_db_object)
        commentedithistory = self.__get_commentedithistory_from_temp_merge_id(from_db_obj=from_db_object)
        if comment:
            group_comment_edit_history_kwargs = model_to_dict(from_db_object, exclude=[
                'id', 'pk', 'group_comment', 'group_comment_id', 'comment', 'comment_id', 'commentedithistory_ptr_id',
                'commentedithistory_ptr', 'edited_by'])
            group_comment_edit_history = group_models.GroupCommentEditHistory(**group_comment_edit_history_kwargs)
            group_comment_edit_history.group_comment_id = comment.id
            group_comment_edit_history.comment_id = comment.id
            group_comment_edit_history.edited_by_id = commentedithistory.edited_by.id
            group_comment_edit_history.commentedithistory_ptr_id = commentedithistory.id
            self.save_object(obj=group_comment_edit_history)
        else:
            raise ValueError('Comments and GroupComments must be imported before GroupCommentEditHistory')
