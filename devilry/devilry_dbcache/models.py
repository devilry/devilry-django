from django.db import models

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.models import FeedbackSet


class AssignmentGroupCachedData(models.Model):
    # NOTE: We may need to reverse this relationship (a cached_data field on AssignmentGroup)
    group = models.OneToOneField(AssignmentGroup, related_name='cached_data')
    first_feedbackset = models.ForeignKey(FeedbackSet, related_name='+',
                                          null=True, blank=True)
    last_feedbackset = models.ForeignKey(FeedbackSet, related_name='+',
                                         null=True, blank=True)
    last_published_feedbackset = models.ForeignKey(FeedbackSet, related_name='+',
                                                   null=True, blank=True)

    #: Number of FeedbackSets with :obj:`~devilry.devilry_group.models.FeedbackSet.feedbackset_type`
    #: set to :obj:`~devilry.devilry_group.models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT`.
    new_attempt_count = models.PositiveIntegerField(default=0)

    public_total_comment_count = models.PositiveIntegerField(default=0)
    public_student_comment_count = models.PositiveIntegerField(default=0)
    public_examiner_comment_count = models.PositiveIntegerField(default=0)
    public_admin_comment_count = models.PositiveIntegerField(default=0)

    public_total_imageannotationcomment_count = models.PositiveIntegerField(default=0)
    public_student_imageannotationcomment_count = models.PositiveIntegerField(default=0)
    public_examiner_imageannotationcomment_count = models.PositiveIntegerField(default=0)
    public_admin_imageannotationcomment_count = models.PositiveIntegerField(default=0)

    #: Number of files uploaded by a student on a
    #: comment that is visible to everyone on the assignment.
    # file_upload_count_student = models.PositiveIntegerField(default=0)
    public_student_file_upload_count = models.PositiveIntegerField(default=0)

    @property
    def last_published_feedbackset_is_last_feedbackset(self):
        """
        Returns ``True`` if :obj:`~.AssignmentGroup.last_published_feedbackset`
        is the same as :obj:`~.AssignmentGroup.last_feedbackset`.
        """
        return self.last_published_feedbackset_id == self.last_feedbackset_id

    @property
    def public_total_anytype_comment_comment_count(self):
        return self.public_total_comment_count + self.public_total_imageannotationcomment_count

    @property
    def public_student_anytype_comment_comment_count(self):
        return self.public_student_comment_count + self.public_student_imageannotationcomment_count

    @property
    def public_examiner_anytype_comment_comment_count(self):
        return self.public_examiner_comment_count + self.public_examiner_imageannotationcomment_count

    @property
    def public_admin_anytype_comment_comment_count(self):
        return self.public_admin_comment_count + self.public_admin_imageannotationcomment_count

    @property
    def last_feedbackset_deadline_datetime(self):
        if self.last_feedbackset == self.first_feedbackset:
            return self.group.assignment.first_deadline
        else:
            return self.last_feedbackset.deadline_datetime
