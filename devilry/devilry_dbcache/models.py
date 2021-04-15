from django.db import models
from django.utils.translation import pgettext_lazy

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
                                 editable=False, on_delete=models.CASCADE)

    #: The first :class:`devilry.devilry_group.models.FeedbackSet` in the
    #: group.
    first_feedbackset = models.ForeignKey(FeedbackSet, related_name='+',
                                          null=True, blank=True, editable=False, on_delete=models.CASCADE)

    #: The last :class:`devilry.devilry_group.models.FeedbackSet` in the
    #: group.
    last_feedbackset = models.ForeignKey(FeedbackSet, related_name='+',
                                         null=True, blank=True, editable=False, on_delete=models.CASCADE)

    #: The last :class:`devilry.devilry_group.models.FeedbackSet` in the
    #: group with a :obj:`~devilry.devilry_group.models.FeedbackSet.grading_published_datetime`.
    #: This also means that the FeedbackSet has
    #: :obj:`~devilry.devilry_group.models.FeedbackSet.grading_points`.
    last_published_feedbackset = models.ForeignKey(FeedbackSet, related_name='+',
                                                   null=True, blank=True, editable=False, on_delete=models.CASCADE)

    #: Number of FeedbackSets with :obj:`~devilry.devilry_group.models.FeedbackSet.feedbackset_type`
    #: set to :obj:`~devilry.devilry_group.models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT`.
    new_attempt_count = models.PositiveIntegerField(
        default=0, editable=False)

    #: The number of :class:`devilry.devilry_group.models.GroupComment` and
    #: :class:`devilry.devilry_group.models.ImageAnnotationComment` within the group
    #: with :obj:`~devilry.devilry_group.models.AbstractGroupComment.visibility`
    #: set to :obj:`~devilry.devilry_group.models.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`
    #: within the group.
    public_total_comment_count = models.PositiveIntegerField(
        default=0, editable=False)

    #: The number of :class:`devilry.devilry_group.models.GroupComment` and
    #: :class:`devilry.devilry_group.models.ImageAnnotationComment` within the group
    #: with :obj:`~devilry.devilry_group.models.AbstractGroupComment.visibility`
    #: set to :obj:`~devilry.devilry_group.models.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`
    #: and :obj:`~devilry.devilry_comment.models.Comment.user_role` set
    #: to :obj:`~devilry.devilry_comment.models.Comment.USER_ROLE_STUDENT`.
    public_student_comment_count = models.PositiveIntegerField(
        default=0, editable=False)

    #: The number of :class:`devilry.devilry_group.models.GroupComment` and
    #: :class:`devilry.devilry_group.models.ImageAnnotationComment` within the group
    #: with :obj:`~devilry.devilry_group.models.AbstractGroupComment.visibility`
    #: set to :obj:`~devilry.devilry_group.models.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`
    #: and :obj:`~devilry.devilry_comment.models.Comment.user_role` set
    #: to :obj:`~devilry.devilry_comment.models.Comment.USER_ROLE_EXAMINER`.
    public_examiner_comment_count = models.PositiveIntegerField(
        default=0, editable=False)

    #: The number of :class:`devilry.devilry_group.models.GroupComment` and
    #: :class:`devilry.devilry_group.models.ImageAnnotationComment` within the group
    #: with :obj:`~devilry.devilry_group.models.AbstractGroupComment.visibility`
    #: set to :obj:`~devilry.devilry_group.models.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`
    #: and :obj:`~devilry.devilry_comment.models.Comment.user_role` set
    #: to :obj:`~devilry.devilry_comment.models.Comment.USER_ROLE_ADMIN`.
    public_admin_comment_count = models.PositiveIntegerField(
        default=0, editable=False)

    #: Number of files uploaded by a student on a
    #: comment that is visible to everyone on the assignment.
    # file_upload_count_student = models.PositiveIntegerField(default=0)
    public_student_file_upload_count = models.PositiveIntegerField(
        default=0, editable=False)

    #: Datetime of the last :class:`devilry.devilry_group.models.GroupComment` or
    #: :class:`devilry.devilry_group.models.ImageAnnotationComment` within the group
    #: with :obj:`~devilry.devilry_group.models.AbstractGroupComment.visibility`
    #: set to :obj:`~devilry.devilry_group.models.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`
    #: and :obj:`~devilry.devilry_comment.models.Comment.user_role` set
    #: to :obj:`~devilry.devilry_comment.models.Comment.USER_ROLE_STUDENT`.
    last_public_comment_by_student_datetime = models.DateTimeField(
        null=True, blank=True, editable=False)

    #: Datetime of the last :class:`devilry.devilry_group.models.GroupComment` or
    #: :class:`devilry.devilry_group.models.ImageAnnotationComment` within the group
    #: with :obj:`~devilry.devilry_group.models.AbstractGroupComment.visibility`
    #: set to :obj:`~devilry.devilry_group.models.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`
    #: and :obj:`~devilry.devilry_comment.models.Comment.user_role` set
    #: to :obj:`~devilry.devilry_comment.models.Comment.USER_ROLE_EXAMINER`.
    last_public_comment_by_examiner_datetime = models.DateTimeField(
        null=True, blank=True, editable=False)

    #: The number of :class:`core.Examiner' within the group
    examiner_count = models.PositiveIntegerField(default=0, editable=False)

    #: The number of :class:`core.Candidate` within the group
    candidate_count = models.PositiveIntegerField(default=0, editable=False)

    @property
    def last_published_feedbackset_is_last_feedbackset(self):
        """
        Returns ``True`` if :obj:`~.AssignmentGroup.last_published_feedbackset`
        is the same as :obj:`~.AssignmentGroup.last_feedbackset`.
        """
        return self.last_published_feedbackset_id == self.last_feedbackset_id

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
        return self.last_feedbackset.deadline_datetime

    @property
    def prettyformat_current_attempt_number(self):
        """
        Format the current attempt number as a human readable string
        suitable for display in a UI.
        """
        if self.new_attempt_count == 0:
            return pgettext_lazy('devilry attempt number', 'first attempt')
        elif self.new_attempt_count == 1:
            return pgettext_lazy('devilry attempt number', 'second attempt')
        elif self.new_attempt_count == 2:
            return pgettext_lazy('devilry attempt number', 'third attempt')
        elif self.new_attempt_count == 4:
            return pgettext_lazy('devilry attempt number', 'fourth attempt')
        else:
            return pgettext_lazy(
                'devilry attempt number',
                '%(attempt_number)sst attempt') % {
                'attempt_number': self.new_attempt_count + 1
            }
