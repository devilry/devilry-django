import json

from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy

from devilry.devilry_comment import models as comment_models
from devilry.apps.core.models import assignment_group


class AbstractGroupCommentQuerySet(models.QuerySet):
    """
    Base class for QuerySets for :class:`.AbstractGroupComment`.
    """
    def exclude_private_comments_from_other_users(self, user):
        return self.exclude(
            models.Q(visibility=AbstractGroupComment.VISIBILITY_PRIVATE) &
            ~models.Q(user=user)
        )

    def exclude_is_part_of_grading_feedbackset_unpublished(self):
        return self.exclude(
            part_of_grading=True,
            feedback_set__grading_published_datetime__isnull=True
        )


class AbstractGroupComment(comment_models.Comment):
    """
    The abstract superclass of all comments related to a delivery and feedback
    """

    #: The related feedbackset. See :class:`.FeedbackSet`.
    feedback_set = models.ForeignKey('FeedbackSet')

    #: If this is ``True``, the comment is published when the feedbackset
    #: is published. This means that this comment is part of the feedback/grading
    #: from the examiner. The same :obj:`~.AbstractGroupComment.visibility`
    #: rules apply no matter if this is ``True`` or ``False``,
    #: this only controls when the comment is published.
    part_of_grading = models.BooleanField(default=False)

    #: Comment only visible for :obj:`~devilry_comment.models.Comment.user` that created comment.
    #: Choice for :obj:`~.AbstractGroupComment.visibility`.
    VISIBILITY_PRIVATE = 'private'

    #: Comment should only be visible to examiners and admins that has
    #: access to the :obj:`~.AbstractGroupComment.feedback_set`.
    #: Choice for :obj:`~.AbstractGroupComment.visibility`.
    VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS = 'visible-to-examiner-and-admins'

    #: Comment should be visible to everyone that has
    #: access to the :obj:`~.AbstractGroupComment.feedback_set`.
    #: Choice for :obj:`~.AbstractGroupComment.visibility`.
    VISIBILITY_VISIBLE_TO_EVERYONE = 'visible-to-everyone'

    #: Choice list.
    #: Choices for :obj:`~.AbstractGroupComment.visibility`.
    VISIBILITY_CHOICES = [
        (VISIBILITY_PRIVATE, 'Private'),
        (VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS, 'Visible to examiners and admins'),
        (VISIBILITY_VISIBLE_TO_EVERYONE, 'Visible to everyone'),
    ]

    #: Sets the visibility choise of the comment.
    #: Defaults to :obj:`~.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`.
    visibility = models.CharField(
        max_length=50,
        db_index=True,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_VISIBLE_TO_EVERYONE,
    )

    class Meta:
        abstract = True

    def get_published_datetime(self):
        """
        Get the publishing datetime of the comment. Publishing datetime is
        the publishing time of the FeedbackSet if the comment has
        :obj:`~devilry.devilry_group.models.AbstractGroupComment.part_of_grading`
        set to True.

        Returns: Datetime.

        """
        return self.feedback_set.grading_published_datetime \
            if self.part_of_grading \
            else self.published_datetime

    def publish_draft(self, time):
        self.published_datetime = time + timezone.timedelta(milliseconds=1)
        self.full_clean()
        self.save()


class FeedbackSet(models.Model):
    """
    All comments that are given for a specific deadline (delivery and feedback) are
    linked to a feedback-set.

    If the comment has `instant_publish=True` it will be published instantly, otherwise the comments will only be
    visible once the feedbackset is published.
    All student-comments will be `instant_publish=True`, and the same applies to comments made by examiners that
    are not a part of feedback.
    """

    #: The AssignmentGroup that owns this feedbackset.
    group = models.ForeignKey(assignment_group.AssignmentGroup)

    #: Is the last feedbackset for :obj:`~.FeedbackSet.group`? Must be None or True.
    is_last_in_group = models.NullBooleanField(default=True)

    #: This means the feedbackset is basically the first feedbackset.
    #: Choice for :obj:`~.FeedbackSet.feedbackset_type`.
    FEEDBACKSET_TYPE_FIRST_ATTEMPT = 'first_attempt'

    #: Is not the first feedbackset, but a new attempt.
    #: Choice for :obj:`~.FeedbackSet.feedbackset_type`
    FEEDBACKSET_TYPE_NEW_ATTEMPT = 'new_attempt'

    #: Something went wrong on grading, with this option, a new
    #: deadline should not be given to student. Student should just
    #: get notified that a new feedback was given.
    #: Choice for :obj:`~.FeedbackSet.feedbackset_type`.
    FEEDBACKSET_TYPE_RE_EDIT = 're_edit'

    #: Grading status choices for :obj:`~.FeedbackSet.feedbackset_type`.
    FEEDBACKSET_TYPE_CHOICES = [
        (FEEDBACKSET_TYPE_FIRST_ATTEMPT, 'first attempt'),
        (FEEDBACKSET_TYPE_NEW_ATTEMPT,'new attempt'),
        (FEEDBACKSET_TYPE_RE_EDIT, 're edit'),
    ]

    #: Sets the type of the feedbackset.
    #: Defaults to :obj:`~.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT`.
    feedbackset_type = models.CharField(
        max_length=50,
        db_index=True,
        choices=FEEDBACKSET_TYPE_CHOICES,
        default=FEEDBACKSET_TYPE_FIRST_ATTEMPT,
    )

    #: The User that created the feedbackset. Only used as metadata
    #: for superusers (for debugging).
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="created_feedbacksets",
                                   null=True, blank=True)

    #: The datetime when this FeedbackSet was created.
    created_datetime = models.DateTimeField(default=timezone.now)

    #: The datetime of the deadline.
    #: The first feedbackset in an AssignmentGroup
    #: (ordered by :obj:`~.FeedbackSet.created_datetime`) does not
    #: have a deadline. It inherits this from the ``first_deadline`` field
    #: of :class:`devilry.apps.core.models.assignment.Assignment`.
    deadline_datetime = models.DateTimeField(null=True, blank=True)

    #: The datetime when the feedback was published.
    #: Set when an examiner publishes the feedback for this FeedbackSet.
    #:
    #: When this is ``None``, the feedbackset is not published. This means that
    #: no comments with :obj:`.AbstractGroupComment.part_of_grading` set to ``True``
    #: is visible, the grade (extracted from points) is not visible, and this
    #: feedbackset does not count when extracting the latest/active feedback/grade
    #: for the AssignmentGroup.
    grading_published_datetime = models.DateTimeField(
        null=True,
        blank=True
    )

    #: Set when the feedbackset is published by an examiner.
    #: If this is ``None``, the feedback is not published, and
    #: the ``points`` (grade) is not available to the student.
    grading_published_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name="published_feedbacksets",
        null=True, blank=True
    )

    #: Points given by examiner for this feedbackset.
    #: The points on the last published FeedbackSet is the current
    #: grade for the AssignmentGroup.
    grading_points = models.PositiveIntegerField(
        null=True, blank=True
    )

    #: A :class:`django.db.models.TextField` for a gradeform filled or not filled for
    #: FeedbackSet.
    gradeform_data_json = models.TextField(
        null=False, blank=True, default=''
    )

    class Meta:
        unique_together = ('group', 'is_last_in_group')
        # index_together = (
        #     'id', 'created_datetime'
        # )

    def __unicode__(self):
        return u"{} - {} - {} - deadline: {}".format(self.group.assignment, self.feedbackset_type, self.group.long_displayname, self.deadline_datetime)

    def clean(self):
        if self.grading_published_datetime is not None and self.grading_published_by is None:
            raise ValidationError({
                'grading_published_datetime': ugettext_lazy('An assignment can not be published '
                                                            'without being published by someone.'),
            })
        if self.grading_published_datetime is not None and self.grading_points is None:
            raise ValidationError({
                'grading_published_datetime': ugettext_lazy('An assignment can not be published '
                                                            'without providing "points".'),
            })
        if self.is_last_in_group is False:
            raise ValidationError({
                'is_last_in_group': 'is_last_in_group can not be false.'
            })

    @property
    def current_deadline(self):
        if self.feedbackset_type == FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT:
            return self.group.parentnode.first_deadline or self.deadline_datetime
        return self.deadline_datetime

    def publish(self, published_by, grading_points, gradeform_data_json=''):
        """
        Publishes this FeedbackSet and comments that belongs to this feedbackset and that are
        part of the grading.

        :param published_by:
            Who published the feedbackset.

        :param grading_points:
            Points give to student(s).

        :param gradeform_data_json:
            gradeform(coming soon).

        Returns:
            True or False and an error message.

        """
        if published_by is None:
            raise ValueError
        if grading_points is None:
            raise ValueError

        current_deadline = self.current_deadline
        # if self.feedbackset_type == FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT:
        #     current_deadline = self.deadline_datetime or self.group.parentnode.first_deadline
        # elif self.feedbackset_type == FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT:
        #     current_deadline = self.deadline_datetime

        if current_deadline is None:
            return False, 'Cannot publish feedback without a deadline.'

        if current_deadline > timezone.now():
            return False, 'The deadline has not expired. Feedback was saved, but not published.'

        drafted_comments = GroupComment.objects.filter(
                feedback_set=self,
                part_of_grading=True
        ).exclude_private_comments_from_other_users(
            user=published_by
        ).order_by('created_datetime')

        now = timezone.now()
        now_without_seconds = now.replace(second=0, microsecond=0)
        for modifier, draft in enumerate(drafted_comments):
            draft.publish_draft(now_without_seconds + timezone.timedelta(milliseconds=modifier))

        self.grading_points = grading_points
        self.grading_published_datetime = now_without_seconds + timezone.timedelta(
                milliseconds=drafted_comments.count() + 1)
        self.grading_published_by = published_by
        self.full_clean()
        self.save()

        return True, ''

    @property
    def gradeform_data(self):
        if self.gradeform_data_json:
            if not hasattr(self, '_gradeform_data'):
                # Store the decoded gradeform_data to avoid re-decoding the json for
                # each access. We invalidate this cache in the setter.
                self._gradeform_data = json.loads(self.gradeform_data_json)
            return self._gradeform_data
        else:
            return None

    @gradeform_data.setter
    def gradeform_data(self, gradeform_data):
        self.gradeform_data_json = json.dumps(gradeform_data)
        if hasattr(self, '_gradeform_data'):
            delattr(self, '_gradeform_data')


class GroupCommentQuerySet(AbstractGroupCommentQuerySet):
    """
    QuerySet for :class:`.GroupComment`.
    """


class GroupComment(AbstractGroupComment):
    """
    A comment made to an `AssignmentGroup`.
    """
    objects = GroupCommentQuerySet.as_manager()

    def __unicode__(self):
        return u"{} - {} - {}".format(self.feedback_set, self.user_role, self.user)


class ImageAnnotationCommentQuerySet(AbstractGroupCommentQuerySet):
    """
    QuerySet for :class:`.ImageAnnotationComment`.
    """


class ImageAnnotationComment(AbstractGroupComment):
    """
    A comment made on a file, as an annotation
    """
    objects = ImageAnnotationCommentQuerySet.as_manager()

    image = models.ForeignKey(comment_models.CommentFileImage)
    x_coordinate = models.PositiveIntegerField()
    y_coordinate = models.PositiveIntegerField()
