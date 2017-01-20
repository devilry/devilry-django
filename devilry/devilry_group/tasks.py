# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# ievv imports
import os

from ievv_opensource.ievv_batchframework import batchregistry


class GroupCommentCompressAction(batchregistry.Action):
    """
    Compress all files that belong to a :obj:`~devilry_group.models.GroupComment`.

    A task than will be run by `ievv_opensource`s batchframework in celery.
    """
    def execute(self):
        groupcomment = self.kwargs.get('context_object')

        commentfiles = groupcomment.commentfile_set.all()
        archivename = '{}-comment.zip'.format(
            groupcomment.user_role
        )

        # Get backend and path
        from devilry.devilry_compressionutil import backend_registry
        zipfile_backend_class = backend_registry.Registry.get_instance().get('devilry_group_local')
        zipfile_path = os.path.join('%d' % groupcomment.feedback_set.group.id,
                                    '%d' % groupcomment.feedback_set.id,
                                    '%d' % groupcomment.id,
                                    archivename)

        # Get backend instance and set the path
        # to the archive and the archivename.
        zipfile_backend = zipfile_backend_class(
                archive_path=zipfile_path,
                archive_name=archivename,
                readmode=False
        )

        # Write files to archive
        for commentfile in commentfiles:
            zipfile_backend.add_file('{}'.format(commentfile.filename), commentfile.file.file)
        zipfile_backend.close()

        # create archive meta entry
        from devilry.devilry_compressionutil.models import CompressedArchiveMeta
        CompressedArchiveMeta.objects.create_meta(
                instance=groupcomment,
                zipfile_backend=zipfile_backend
        )


class FeedbackSetCompressAction(batchregistry.Action):
    """
    Compress all files that belong to a :obj:`~devilry_group.models.FeedbackSet`.

    A task than will be run by `ievv_opensource`s batchframework in celery.
    """
    def _get_archive_name(self, feedbackset):
        """

        Args:
            feedbackset:

        Returns:

        """
        return '{}-{}-delivery.zip'.format(
            feedbackset.group.parentnode.get_path(),
            feedbackset.current_deadline().format('%Y-%m-%d_%H-%M-%S.%f')
        )

    def _get_archive_path(self, feedbackset, archivename):
        """

        Args:
            feedbackset:
            archivename:

        Returns:

        """
        return os.path.join('%d' % feedbackset.group.id,
                            '%d' % feedbackset.id,
                            archivename)

    def _zipfile_add(self, zipfile_backend, comment_file, feedback_set):
        """

        Args:
            zipfile_backend:
            comment_file:
            feedback_set:

        Returns:

        """
        # Where should the file recide in the zipped archive.
        # The folder the file should be added under is set to 'delivery' by default.
        sub_folder_type = 'delivery'

        if comment_file.comment.user_role == 'student':
            current_deadline = feedback_set.current_deadline()
            if current_deadline and comment_file.comment.published_datetime > current_deadline:
                sub_folder_type = 'uploaded_after_deadline'
        elif comment_file.comment.user_role == 'examiner':
            sub_folder_type = 'uploaded_by_examiner'

        # Write file to backend on the path defined by os.path.join
        zipfile_backend.add_file(
            os.path.join(sub_folder_type, comment_file.filename),
            comment_file.file.file)

    def execute(self):
        """
        The task performed by BatchOperation.

        Returns:

        """
        feedback_set = self.kwargs.get('context_object')

        # Create the name for the actual archive.
        archive_name = self._get_archive_name(feedbackset=feedback_set)

        # Get backend and path
        from devilry.devilry_compressionutil import backend_registry
        zipfile_backend_class = backend_registry.Registry.get_instance().get('devilry_group_local')

        zipfile_path = self._get_archive_path(feedbackset=feedback_set, archivename=archive_name)

        # Get backend instance
        zipfile_backend = zipfile_backend_class(
            archive_path=zipfile_path,
            archive_name=archive_name,
            readmode=False
        )

        # Write files to archive
        from devilry.devilry_group import models as group_models
        for group_comment in feedback_set.groupcomment_set.all():
            # Don't add files from comments that are not visible to everyone.
            if group_comment.visibility == group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE:
                for comment_file in group_comment.commentfile_set.all():
                    self._zipfile_add(zipfile_backend=zipfile_backend,
                                      comment_file=comment_file,
                                      feedback_set=feedback_set)
        zipfile_backend.close()

        # create archive meta entry
        from devilry.devilry_compressionutil.models import CompressedArchiveMeta
        CompressedArchiveMeta.objects.create_meta(
                instance=feedback_set,
                zipfile_backend=zipfile_backend
        )
