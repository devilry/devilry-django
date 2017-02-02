# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from ievv_opensource.ievv_batchframework import batchregistry


class AbstractBaseBatchAction(batchregistry.Action):
    """

    """
    #: Backend id to get from registry in function `get_backend()`.
    #: Must be set in subclass.
    backend_id = ''

    def get_backend(self, zipfile_path, archive_name):
        """
        Get and instance of the backend to use.

        Args:
            zipfile_path: Path to the archive.
            archive_name: Name of the archive.

        Returns:

        """
        from devilry.devilry_compressionutil import backend_registry
        zipfile_backend_class = backend_registry.Registry.get_instance().get(self.backend_id)
        return zipfile_backend_class(
            archive_path=zipfile_path,
            archive_name=archive_name,
            readmode=False
        )

    def add_file(self, zipfile_backend, sub_path, comment_file, current_deadline):
        """
        Args:
            zipfile_backend:
            sub_path:
            comment_file:
            current_deadline:
        """
        sub_folder_type = 'delivery'
        if comment_file.comment.user_role == 'student':
            if current_deadline and comment_file.comment.published_datetime > current_deadline:
                sub_folder_type = 'uploaded_after_deadline'
        elif comment_file.comment.user_role == 'examiner' \
                or comment_file.comment.user_role == 'admin':
            sub_folder_type = 'uploaded_by_examiners_and_admins'

        # Write file to backend on the path defined by os.path.join
        zipfile_backend.add_file(
            os.path.join(sub_path, sub_folder_type, comment_file.filename),
            comment_file.file.file)

    def execute(self):
        raise NotImplementedError()


class FeedbackSetBatchMixin(object):
    """
    Mixin for adding FeedbackSet files to zipfile.

    Must be included in class together with :class:`~.AbstractBaseBatchAction`.
    """
    def zipfile_add_feedbackset(self, zipfile_backend, feedback_set, sub_path=''):
        from devilry.devilry_group import models as group_models
        for group_comment in feedback_set.groupcomment_set.all():
            # Don't add files from comments that are not visible to everyone.
            if group_comment.visibility == group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE:
                for comment_file in group_comment.commentfile_set.all():
                    self.add_file(zipfile_backend=zipfile_backend,
                                  sub_path=sub_path,
                                  comment_file=comment_file,
                                  current_deadline=feedback_set.current_deadline())


class FeedbackSetCompressAction(AbstractBaseBatchAction, FeedbackSetBatchMixin):
    """
    Compress all files that belong to a :obj:`~devilry_group.models.FeedbackSet`.

    A task than will be run by `ievv_opensource`s batchframework in celery.
    """
    backend_id = 'devilry_group_local'

    def execute(self):
        feedback_set = self.kwargs.get('context_object')

        # Create the name for the actual archive.
        from django.utils import timezone
        archive_name = 'feedbackset-{}-{}-delivery.zip'.format(
            feedback_set.id,
            timezone.now().strftime('%Y-%m-%d_%H-%M-%S.%f'))

        # create the path for the archive
        zipfile_path = os.path.join(
            str(feedback_set.group.parentnode.parentnode_id),
            str(feedback_set.group.parentnode.id),
            str(feedback_set.group.id),
            archive_name)

        # Get backend
        zipfile_backend = self.get_backend(zipfile_path=zipfile_path, archive_name=archive_name)

        # Add FeedbackSet files to archive.
        self.zipfile_add_feedbackset(zipfile_backend=zipfile_backend, feedback_set=feedback_set)

        zipfile_backend.close()

        # create archive meta entry
        from devilry.devilry_compressionutil.models import CompressedArchiveMeta
        CompressedArchiveMeta.objects.create_meta(
                instance=feedback_set,
                zipfile_backend=zipfile_backend
        )
