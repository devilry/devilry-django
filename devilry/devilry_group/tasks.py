# -*- coding: utf-8 -*-


import logging
import posixpath

from devilry.devilry_compressionutil.abstract_batch_action import AbstractBaseBatchAction
from devilry.devilry_compressionutil.batchjob_mixins.feedbackset_mixin import FeedbackSetBatchMixin
from devilry.utils.memorydebug import print_memory_usage

logger = logging.getLogger(__name__)


class FeedbackSetCompressAction(AbstractBaseBatchAction, FeedbackSetBatchMixin):
    """
    Compress all files that belong to a :obj:`~devilry_group.models.FeedbackSet`.
    """
    backend_id = 'devilry_group_local'

    def execute(self):
        feedback_set = self.kwargs['context_object']
        try:
            print_memory_usage('Start of RQ task')
            started_by_user = self.kwargs.get('started_by')

            from devilry.devilry_group import models as group_models
            feedback_sets_with_public_student_comments = group_models.FeedbackSet.objects\
                .filter_public_comment_files_from_students().filter(id=feedback_set.id)
            if not feedback_sets_with_public_student_comments.exists():
                # Do nothing
                return

            # Create the name for the actual archive.
            from django.utils import timezone
            archive_name = 'feedbackset-{}-{}-delivery'.format(
                feedback_set.id,
                timezone.now().strftime('%Y-%m-%d_%H-%M-%S.%f'))

            # create the path for the archive
            zipfile_path = posixpath.join(
                str(feedback_set.group.parentnode.parentnode_id),
                str(feedback_set.group.parentnode.id),
                str(feedback_set.group.id),
                archive_name)

            # Get backend
            print_memory_usage('Before initializing zip backend')
            zipfile_backend = self.get_backend(zipfile_path=zipfile_path, archive_name=archive_name)

            # Add FeedbackSet files to archive.
            print_memory_usage('Before adding feedbackset files to zip backend')
            self.zipfile_add_feedbackset(zipfile_backend=zipfile_backend, feedback_set=feedback_set)
            print_memory_usage('After adding feedbackset files to zip backend')

            zipfile_backend.close()
            print_memory_usage('After closing ZIP file')

            # create archive meta entry
            from devilry.devilry_compressionutil.models import CompressedArchiveMeta
            CompressedArchiveMeta.objects.create_meta(
                instance=feedback_set,
                zipfile_backend=zipfile_backend,
                user=started_by_user
            )

            print_memory_usage('End of RQ task')
        except Exception:
            logger.exception(
                'Failed to generate zip archive from feedbackset %s',
                feedback_set.pk)
