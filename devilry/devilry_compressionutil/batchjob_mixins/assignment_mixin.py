# -*- coding: utf-8 -*-


import os

from django.template import defaultfilters

from devilry.devilry_compressionutil.batchjob_mixins import feedbackset_mixin


class AssignmentBatchMixin(feedbackset_mixin.FeedbackSetBatchMixin):
    """
    Mixin for adding FeedbackSet files to zipfile for all AssignmentGroups in the Assignment the user has access to.

    Must be included in class together with
    :class:`devilry.devilry_compressionutil.batchjob_mixins.feedbackset_mixin.FeedbackSetBatchMixin`.
    """
    def get_assignment_group_queryset(self, assignment, user):
        """
        Must be overriden in subclass.

        Get the assignmentgroups from the assignment that the user has access to. Add permission
        filtering here.

        Args:
            assignment: The assignment to fetch groups for.
            user: The "request" user.

        Returns:
            QuerySet: AssignmentGroup queryset.
        """
        raise NotImplementedError()

    def add_assignment_groups(self, user, zipfile_backend, assignment):
        for group in self.get_assignment_group_queryset(assignment=assignment, user=user):
            group_path = '{}'.format(group.get_short_displayname())
            for feedback_set in group.feedbackset_set.all():
                feedback_set_path = 'deadline-{}'.format(defaultfilters.date(feedback_set.current_deadline(), 'Y-m-d-Hi'))
                self.zipfile_add_feedbackset(
                    zipfile_backend=zipfile_backend,
                    feedback_set=feedback_set,
                    sub_path=os.path.join(group_path, feedback_set_path)
                )
