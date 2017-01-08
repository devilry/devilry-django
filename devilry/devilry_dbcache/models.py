from django.db import models

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.models import FeedbackSet


class AssignmentGroupCachedData(models.Model):
    """
    Automatically cached data for an
    :class:`devilry.apps.core.models.assignment_group.AssignmentGroup`.

    This model is automatically maintained via postgres triggers, and
    it should never be edited manually.
    """

    #: The :class:`devilry.apps.core.models.assignment_group.AssignmentGroup`
    #: that this model caches data for.
    group = models.OneToOneField(AssignmentGroup, related_name='cached_data',
                                 editable=False)

    #: The first :class:`devilry.devilry_group.models.FeedbackSet` in the
    #: group.
    first_feedbackset = models.ForeignKey(FeedbackSet, related_name='+',
                                          null=True, blank=True, editable=False)

    #: The last :class:`devilry.devilry_group.models.FeedbackSet` in the
    #: group.
    last_feedbackset = models.ForeignKey(FeedbackSet, related_name='+',
                                         null=True, blank=True, editable=False)

    #: The last :class:`devilry.devilry_group.models.FeedbackSet` in the
    #: group with a :obj:`~devilry.devilry_group.models.FeedbackSet.grading_published_datetime`.
    #: This also means that the FeedbackSet has
    #: :obj:`~devilry.devilry_group.models.FeedbackSet.grading_points`.
    last_published_feedbackset = models.ForeignKey(FeedbackSet, related_name='+',
                                                   null=True, blank=True, editable=False)

    #: Number of FeedbackSets with :obj:`~devilry.devilry_group.models.FeedbackSet.feedbackset_type`
    #: set to :obj:`~devilry.devilry_group.models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT`.
    new_attempt_count = models.PositiveIntegerField(
        default=0, editable=False)

    #: The number of :class:`devilry.devilry_group.models.GroupComment` within the group
    #: with :obj:`~devilry.devilry_group.models.AbstractGroupComment.visibility`
    #: set to :obj:`~devilry.devilry_group.models.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`
    #: within the group.
    public_total_comment_count = models.PositiveIntegerField(
        default=0, editable=False)

    #: The number of :class:`devilry.devilry_group.models.GroupComment` within the group
    #: with :obj:`~devilry.devilry_group.models.AbstractGroupComment.visibility`
    #: set to :obj:`~devilry.devilry_group.models.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`
    #: and :obj:`~devilry.devilry_comment.models.Comment.user_role` set
    #: to :obj:`~devilry.devilry_comment.models.Comment.USER_ROLE_STUDENT`.
    public_student_comment_count = models.PositiveIntegerField(
        default=0, editable=False)

    #: The number of :class:`devilry.devilry_group.models.GroupComment` within the group
    #: with :obj:`~devilry.devilry_group.models.AbstractGroupComment.visibility`
    #: set to :obj:`~devilry.devilry_group.models.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`
    #: and :obj:`~devilry.devilry_comment.models.Comment.user_role` set
    #: to :obj:`~devilry.devilry_comment.models.Comment.USER_ROLE_EXAMINER`.
    public_examiner_comment_count = models.PositiveIntegerField(
        default=0, editable=False)

    #: The number of :class:`devilry.devilry_group.models.GroupComment` within the group
    #: with :obj:`~devilry.devilry_group.models.AbstractGroupComment.visibility`
    #: set to :obj:`~devilry.devilry_group.models.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`
    #: and :obj:`~devilry.devilry_comment.models.Comment.user_role` set
    #: to :obj:`~devilry.devilry_comment.models.Comment.USER_ROLE_ADMIN`.
    public_admin_comment_count = models.PositiveIntegerField(
        default=0, editable=False)

    #: The number of :class:`devilry.devilry_group.models.ImageAnnotationComment` within the group
    #: with :obj:`~devilry.devilry_group.models.AbstractGroupComment.visibility`
    #: set to :obj:`~devilry.devilry_group.models.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`
    #: within the group.
    public_total_imageannotationcomment_count = models.PositiveIntegerField(
        default=0, editable=False)

    #: The number of :class:`devilry.devilry_group.models.ImageAnnotationComment` within the group
    #: with :obj:`~devilry.devilry_group.models.AbstractGroupComment.visibility`
    #: set to :obj:`~devilry.devilry_group.models.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`
    #: and :obj:`~devilry.devilry_comment.models.Comment.user_role` set
    #: to :obj:`~devilry.devilry_comment.models.Comment.USER_ROLE_STUDENT`.
    public_student_imageannotationcomment_count = models.PositiveIntegerField(
        default=0, editable=False)

    #: The number of :class:`devilry.devilry_group.models.ImageAnnotationComment` within the group
    #: with :obj:`~devilry.devilry_group.models.AbstractGroupComment.visibility`
    #: set to :obj:`~devilry.devilry_group.models.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`
    #: and :obj:`~devilry.devilry_comment.models.Comment.user_role` set
    #: to :obj:`~devilry.devilry_comment.models.Comment.USER_ROLE_EXAMINER`.
    public_examiner_imageannotationcomment_count = models.PositiveIntegerField(
        default=0, editable=False)

    #: The number of :class:`devilry.devilry_group.models.ImageAnnotationComment` within the group
    #: with :obj:`~devilry.devilry_group.models.AbstractGroupComment.visibility`
    #: set to :obj:`~devilry.devilry_group.models.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`
    #: and :obj:`~devilry.devilry_comment.models.Comment.user_role` set
    #: to :obj:`~devilry.devilry_comment.models.Comment.USER_ROLE_ADMIN`.
    public_admin_imageannotationcomment_count = models.PositiveIntegerField(
        default=0, editable=False)

    #: Number of files uploaded by a student on a
    #: comment that is visible to everyone on the assignment.
    # file_upload_count_student = models.PositiveIntegerField(default=0)
    public_student_file_upload_count = models.PositiveIntegerField(
        default=0, editable=False)

    @property
    def last_published_feedbackset_is_last_feedbackset(self):
        """
        Returns ``True`` if :obj:`~.AssignmentGroup.last_published_feedbackset`
        is the same as :obj:`~.AssignmentGroup.last_feedbackset`.
        """
        return self.last_published_feedbackset_id == self.last_feedbackset_id

    @property
    def public_total_anytype_comment_comment_count(self):
        """
        Returns :obj:`~.AssignmentGroupCachedData.public_total_comment_count` +
        :obj:`~.AssignmentGroupCachedData.public_total_imageannotationcomment_count`.
        """
        return self.public_total_comment_count + self.public_total_imageannotationcomment_count

    @property
    def public_student_anytype_comment_comment_count(self):
        """
        Returns :obj:`~.AssignmentGroupCachedData.public_student_comment_count` +
        :obj:`~.AssignmentGroupCachedData.public_student_imageannotationcomment_count`.
        """
        return self.public_student_comment_count + self.public_student_imageannotationcomment_count

    @property
    def public_examiner_anytype_comment_comment_count(self):
        """
        Returns :obj:`~.AssignmentGroupCachedData.public_examiner_comment_count` +
        :obj:`~.AssignmentGroupCachedData.public_examiner_imageannotationcomment_count`.
        """
        return self.public_examiner_comment_count + self.public_examiner_imageannotationcomment_count

    @property
    def public_admin_anytype_comment_comment_count(self):
        """
        Returns :obj:`~.AssignmentGroupCachedData.public_admin_comment_count` +
        :obj:`~.AssignmentGroupCachedData.public_admin_imageannotationcomment_count`.
        """
        return self.public_admin_comment_count + self.public_admin_imageannotationcomment_count

    @property
    def last_feedbackset_deadline_datetime(self):
        """
        Get the deadline of the last :class:`devilry.devilry_group.models.FeedbackSet`
        in the group.

        This is the active deadline for the group.

        If the last feedbackset is the first feedbackset this returns
        :obj:`devilry.apps.core.models.assignment.Assignment.first_deadline`,
        otherwise it returns the
        :obj:`devilry.devilry_group.models.FeedbackSet.deadline_datetime` of the
        last feedbackset.
        """
        if self.last_feedbackset == self.first_feedbackset:
            return self.group.assignment.first_deadline
        else:
            return self.last_feedbackset.deadline_datetime
