# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# ievv imports
from ievv_opensource.ievv_batchframework import batchregistry


class GroupCommentCompressAction(batchregistry.Action):
    """

    """
    def execute(self):
        """

        """
        groupcomment = self.kwargs.get('context_object')

        commentfiles = groupcomment.commentfile_set.all()
        archivename = '{}-{}.zip'.format(
            groupcomment.user_role,
            groupcomment.user
        )

        # Get backend and path
        from devilry.devilry_ziputil import backend_registry
        zipfile_backend_class = backend_registry.Registry.get_instance().get('devilry_group_local')
        zipfile_path = '{}/{}/{}/{}'.format(groupcomment.feedback_set.group.id,
                                            groupcomment.feedback_set.id,
                                            groupcomment.id,
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
        from devilry.devilry_ziputil.models import CompressedArchiveMeta
        CompressedArchiveMeta.objects.create_meta(
                instance=groupcomment,
                zipfile_backend=zipfile_backend
        )


class FeedbackSetCompressAction(batchregistry.Action):
    """

    """
    def execute(self):
        """

        Returns:

        """
        feedbackset = self.kwargs.get('context_object')

        archivename = '{}-{}-delivery.zip'.format(
            feedbackset.group.parentnode.get_path(),
            feedbackset.current_deadline()
        )

        # Get backend and path
        from devilry.devilry_ziputil import backend_registry
        zipfile_backend_class = backend_registry.Registry.get_instance().get('devilry_group_local')
        zipfile_path = '{}/{}/{}'.format(feedbackset.group.id,
                                         feedbackset.id,
                                         archivename)

        # Get backend instance
        zipfile_backend = zipfile_backend_class(
            archive_path=zipfile_path,
            archive_name=archivename,
            readmode=False
        )

        # Write files to archive
        from devilry.devilry_group import models as group_models
        for group_comment in feedbackset.groupcomment_set.all():
            # Don't add files from comments that are not visible to everyone.
            if group_comment.visibility == group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE:
                for comment_file in group_comment.commentfile_set.all():
                    if comment_file.comment.user_role == 'student':
                        if comment_file.comment.published_datetime > feedbackset.current_deadline():
                            zipfile_backend.add_file('uploaded_after_deadline/{}'.format(comment_file.filename),
                                                     comment_file.file.file)
                        else:
                            zipfile_backend.add_file('delivery/{}'.format(comment_file.filename),
                                                     comment_file.file.file)
        zipfile_backend.close()

        # create archive meta entry
        from devilry.devilry_ziputil.models import CompressedArchiveMeta
        CompressedArchiveMeta.objects.create_meta(
                instance=feedbackset,
                zipfile_backend=zipfile_backend
        )
