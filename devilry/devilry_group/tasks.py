# -*- coding: utf-8 -*-


import os

from devilry.devilry_compressionutil.abstract_batch_action import AbstractBaseBatchAction
from devilry.devilry_compressionutil.batchjob_mixins.feedbackset_mixin import FeedbackSetBatchMixin


class FeedbackSetCompressAction(AbstractBaseBatchAction, FeedbackSetBatchMixin):
    """
    Compress all files that belong to a :obj:`~devilry_group.models.FeedbackSet`.
    """
    backend_id = 'devilry_group_local'

    def execute(self):
        feedback_set = self.kwargs.get('context_object')
        started_by_user = self.kwargs.get('started_by')

        from devilry.devilry_group import models as group_models
        feedback_sets_with_public_student_comments = group_models.FeedbackSet.objects\
            .filter_public_comment_files_from_students().filter(id=feedback_set.id)
        if not feedback_sets_with_public_student_comments.exists():
            # Do nothing
            return

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
            zipfile_backend=zipfile_backend,
            user=started_by_user
        )
