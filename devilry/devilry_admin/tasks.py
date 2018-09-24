# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from devilry.devilry_compressionutil.abstract_batch_action import AbstractBaseBatchAction
from devilry.devilry_compressionutil.batchjob_mixins.assignment_mixin import AssignmentBatchMixin


class AssignmentCompressAction(AbstractBaseBatchAction, AssignmentBatchMixin):
    backend_id = 'devilry_admin_local'

    def get_assignment_group_queryset(self, assignment, user):
        return assignment.assignmentgroups.filter_user_is_admin(user=user)

    def execute(self):
        assignment = self.kwargs.get('context_object')
        started_by_user = self.kwargs.get('started_by')

        from devilry.devilry_group import models as group_models
        feedback_sets_with_public_student_comments = group_models.FeedbackSet.objects \
            .filter_public_comment_files_from_students()\
            .filter(group__parentnode=assignment)
        if not feedback_sets_with_public_student_comments.exists():
            # Do nothing
            return

        # Create name for the actual archive
        from django.utils import timezone
        archive_name = '{}.{}.{}.{}.zip'.format(
            assignment.subject.short_name,
            assignment.period.short_name,
            assignment.short_name,
            timezone.now().strftime('%Y-%m-%d_%H-%M-%S.%f'))

        # create path for the archive.
        zipfile_path = os.path.join(
            'admin',
            str(assignment.parentnode.id),
            str(assignment.id),
            str(started_by_user.id),
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
            zipfile_backend=zipfile_backend,
            user=started_by_user,
            user_role=CompressedArchiveMeta.CREATED_BY_ROLE_ADMIN
        )
