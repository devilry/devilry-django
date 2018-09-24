# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os


class FeedbackSetBatchMixin(object):
    """
    Mixin for adding FeedbackSet files to zipfile.

    Must be included in class together with
    :class:`devilry.devilry_compressionutil.abstract_batch_action.AbstractBaseBatchAction`.
    """
    def __build_zip_archive_from_comment_file_tree(self, zipfile_backend, sub_path, comment_file_tree):
        for filename, value in comment_file_tree.iteritems():
            # Add files before deadline
            if value['before_deadline']['last']:
                comment_file = value['before_deadline']['last']
                self.add_file(zipfile_backend=zipfile_backend,
                              sub_path=sub_path,
                              comment_file=comment_file)
                for old_duplicate in value['before_deadline']['old_duplicates']:
                    self.add_file(zipfile_backend=zipfile_backend,
                                  sub_path=os.path.join(sub_path, 'old_duplicates'),
                                  comment_file=old_duplicate,
                                  is_duplicate=True)

            # Add files after deadline
            if value['after_deadline']['last']:
                comment_file = value['after_deadline']['last']
                after_deadline_sub_path = os.path.join(sub_path, 'after_deadline_not_part_of_delivery')
                self.add_file(zipfile_backend=zipfile_backend,
                              sub_path=after_deadline_sub_path,
                              comment_file=comment_file)
                for old_duplicate in value['after_deadline']['old_duplicates']:
                    self.add_file(zipfile_backend=zipfile_backend,
                                  sub_path=os.path.join(after_deadline_sub_path, 'old_duplicates'),
                                  comment_file=old_duplicate,
                                  is_duplicate=True)

    def zipfile_add_feedbackset(self, zipfile_backend, feedback_set, sub_path=''):
        from devilry.devilry_group import models as group_models

        comment_file_tree = {}
        for group_comment in feedback_set.groupcomment_set.all().order_by('-created_datetime'):
            # Don't add files from comments that are not visible to everyone.
            if group_comment.visibility == group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE and \
                    group_comment.user_role == group_models.GroupComment.USER_ROLE_STUDENT:
                for comment_file in group_comment.commentfile_set.all().order_by('-created_datetime'):
                    filename = comment_file.filename
                    if comment_file.filename not in comment_file_tree:
                        comment_file_tree[filename] = {
                            'before_deadline': {
                                'last': None,
                                'old_duplicates': []
                            },
                            'after_deadline': {
                                'last': None,
                                'old_duplicates': []
                            }
                        }

                    if group_comment.published_datetime <= feedback_set.deadline_datetime:
                        # Before the deadline expired
                        # Set initial last delivery before deadline, and duplicates.
                        if comment_file_tree[filename]['before_deadline']['last'] is None:
                            comment_file_tree[filename]['before_deadline']['last'] = comment_file
                        else:
                            comment_file_tree[filename]['before_deadline']['old_duplicates'].append(comment_file)

                    else:
                        # After the deadline expired.
                        # Set initial last delivery after deadline, and duplicates.
                        if comment_file_tree[filename]['after_deadline']['last'] is None:
                            comment_file_tree[filename]['after_deadline']['last'] = comment_file
                        else:
                            comment_file_tree[filename]['after_deadline']['old_duplicates'].append(comment_file)

        # Start building the ZIP archive.
        self.__build_zip_archive_from_comment_file_tree(
            zipfile_backend=zipfile_backend,
            sub_path=sub_path,
            comment_file_tree=comment_file_tree,
        )