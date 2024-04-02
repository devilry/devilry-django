# -*- coding: utf-8 -*-


import os

from django.db.models import Prefetch, F

from devilry.devilry_group.models import GroupComment, FeedbackSet
from devilry.devilry_comment.models import CommentFile


class FeedbackSetBatchMixin(object):
    """
    Mixin for adding FeedbackSet files to zipfile.

    Must be included in class together with
    :class:`devilry.devilry_compressionutil.abstract_batch_action.AbstractBaseBatchAction`.
    """

    def add_file(self, zipfile_backend, sub_path, comment_file, is_duplicate=False):
        """
        Add file to ZIP archive.

        Args:
            zipfile_backend: A subclass of ``PythonZipFileBackend``.
            sub_path: The path to write to inside the archive.
            comment_file: The `CommentFile` file to write.
            is_duplicate: Is the file a duplicate? Defaults to ``False``.
        """
        file_name = comment_file.filename
        if is_duplicate:
            file_name = comment_file.get_filename_as_unique_string()

        zipfile_backend.add_file(
            os.path.join(sub_path, file_name),
            comment_file.file)

    def get_feedbackset_queryset(self):
        commentfile_queryset = CommentFile.objects.all().order_by('-created_datetime') \
            .only('filename', 'file', 'created_datetime', 'comment_id')

        groupcomment_queryset = GroupComment.objects \
            .filter(
                visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                user_role=GroupComment.USER_ROLE_STUDENT
            ) \
            .only('comment_ptr_id', 'feedback_set_id', 'published_datetime') \
            .order_by('-created_datetime') \
            .prefetch_related(
                Prefetch(
                    'commentfile_set',
                    queryset=commentfile_queryset,
                )
            )

        return FeedbackSet.objects.all().only('deadline_datetime', 'group_id') \
            .prefetch_related(
                Prefetch(
                    'groupcomment_set',
                    queryset=groupcomment_queryset,
                )
        )

    def zipfile_add_feedbackset(self, zipfile_backend, feedback_set, sub_path=''):
        duplicates_sub_path = os.path.join(sub_path, 'old_duplicates')
        after_deadline_sub_path = os.path.join(sub_path, 'after_deadline_not_part_of_delivery')
        after_deadline_duplicates_sub_path = os.path.join(after_deadline_sub_path, 'old_duplicates')
        comment_file_tree = {}
        for group_comment in feedback_set.groupcomment_set.all():
            for comment_file in group_comment.commentfile_set.all():
                filename = comment_file.filename
                if filename not in comment_file_tree:
                    comment_file_tree[filename] = {
                        'before_deadline': {
                            'last': False,
                        },
                        'after_deadline': {
                            'last': False,
                        }
                    }
                # Before the deadline expired
                # Set initial last delivery before deadline, and duplicates.
                if group_comment.published_datetime <= feedback_set.deadline_datetime:
                    if comment_file_tree[filename]['before_deadline']['last'] is False:
                        comment_file_tree[filename]['before_deadline']['last'] = True
                        self.add_file(zipfile_backend=zipfile_backend,
                                      sub_path=sub_path,
                                      comment_file=comment_file)
                    else:
                        self.add_file(zipfile_backend=zipfile_backend,
                                      sub_path=duplicates_sub_path,
                                      comment_file=comment_file,
                                      is_duplicate=True)
                else:
                    if comment_file_tree[filename]['after_deadline']['last'] is False:
                        comment_file_tree[filename]['after_deadline']['last'] = True
                        self.add_file(zipfile_backend=zipfile_backend,
                                      sub_path=after_deadline_sub_path,
                                      comment_file=comment_file)
                    else:
                        self.add_file(zipfile_backend=zipfile_backend,
                                      sub_path=after_deadline_duplicates_sub_path,
                                      comment_file=comment_file,
                                      is_duplicate=True)
