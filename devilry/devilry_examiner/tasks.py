# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from devilry.devilry_group.tasks import AbstractBaseBatchAction, FeedbackSetBatchMixin


class AssignmentBatchMixin(object):
    """
    Mixin for adding FeedbackSet files to zipfile for all AssignmentGroups in the Assignment.

    Must be included in class together with :class:`~.FeedbackSetBatchMixin`.
    """
    def add_assignment_groups(self, user, zipfile_backend, assignment):
        for group in assignment.assignmentgroups.filter_examiner_has_access(user=user):
            group_path = 'group-{}'.format(group)
            for feedback_set in group.feedbackset_set.all():
                feedback_set_path = 'deadline{}'.format(feedback_set.current_deadline())
                self.zipfile_add_feedbackset(
                    zipfile_backend=zipfile_backend,
                    feedback_set=feedback_set,
                    sub_path=os.path.join(group_path, feedback_set_path)
                )


class AssignmentCompressAction(AbstractBaseBatchAction, AssignmentBatchMixin, FeedbackSetBatchMixin):
    backend_id = 'devilry_examiner_local'

    def execute(self):
        assignment = self.kwargs.get('context_object')
        started_by_user = self.kwargs.get('started_by')

        # Create name for the actual archive
        from django.utils import timezone
        archive_name = '{}-{}.zip'.format(
            assignment.short_name,
            timezone.now().strftime('%Y-%m-%d_%H-%M-%S.%f'))

        # create path for the archive.
        zipfile_path = os.path.join(
            str(assignment.parentnode.id),
            str(assignment.id),
            archive_name
        )

        # get backend
        zipfile_backend = self.get_backend(zipfile_path=zipfile_path, archive_name=archive_name)

        self.add_assignment_groups(user=started_by_user, zipfile_backend=zipfile_backend, assignment=assignment)

        zipfile_backend.close()

        # create archive meta entry
        from devilry.devilry_compressionutil.models import CompressedArchiveMeta
        CompressedArchiveMeta.objects.create_meta(
            instance=assignment,
            zipfile_backend=zipfile_backend
        )
