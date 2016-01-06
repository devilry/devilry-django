import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy

from devilry.devilry_comment import models as comment_models
from devilry.apps.core.models import assignment_group


class AbstractGroupComment(comment_models.Comment):
    """
    The abstract superclass of all comments related to a delivery and feedback
    """
    feedback_set = models.ForeignKey('FeedbackSet')

    #: If this is ``True``
    instant_publish = models.BooleanField(default=False)

    #: Is the comment visible for students? This is always ``True`` for
    #: comments added by students, but examiners can set this to ``False`` to
    #: save a draft.
    visible_for_students = models.BooleanField(default=False)

    # visibility = models.CharField(
    #     choices=[
    #         ('draft', 'Draft'),
    #         ('visible-to-examiner-and-admins', 'Visible to examiners and admins'),
    #         ('visible-to-everyone', 'Visible to everyone'),
    #     ]
    # )

    class Meta:
        abstract = True


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

    #: The User that created the feedbackset. Only used as metadata
    #: for superusers (for debugging).
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="created_feedbacksets")

    #: The datetime when this FeedbackSet was created.
    created_datetime = models.DateTimeField(default=datetime.datetime.now)

    deadline_datetime = models.DateTimeField(null=True, blank=True)

    #: The datetime when the feedback was published.
    #: Set when an examiner publishes the feedback for this FeedbackSet.
    #:
    #: When this is ``None``, the feedbackset is not published. This means that
    #: no comments from examiners with ``instant_publish=False`` is visible,
    #: and the grade is not visible.
    published_datetime = models.DateTimeField(null=True, blank=True)

    #: Set when the feedbackset is published by an examiner.
    #: If this is ``None``, the feedback is not published, and
    #: the ``points`` (grade) is not available to the student.
    published_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="published_feedbacksets")

    #: Points given by examiner for this feedbackset.
    #: The points on the last published FeedbackSet is the current
    #: grade for the AssignmentGroup.
    points = models.PositiveIntegerField()

    #: A :class:`django.db.models.TextField` for a gradeform filled or not filled for
    #: FeedbackSet.
    gradeform_json = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u"{} - {} - {}".format(self.group.assignment, self.group, self.deadline_datetime)

    def clean(self):
        if self.published_by is not None and self.points is None:
            raise ValidationError({
                'published_by': ugettext_lazy('An assignment can not be published witout providing "points".'),
            })


class GroupComment(AbstractGroupComment):
    """
    A comment made to an `AssignmentGroup`.
    """
    def __unicode__(self):
        return u"{} - {} - {}".format(self.feedback_set, self.user_role, self.user)


class ImageAnnotationComment(AbstractGroupComment):
    """
    A comment made on a file, as an annotation
    """
    image = models.ForeignKey(comment_models.CommentFileImage)
    x_coordinate = models.PositiveIntegerField()
    y_coordinate = models.PositiveIntegerField()
