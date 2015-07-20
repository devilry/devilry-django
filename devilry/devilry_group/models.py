from django.db import models
from devilry.devilry_comment import models as comment_models
from devilry.apps.core.models import assignment_group
from django.contrib.auth import models as auth_models


class AbstractGroupComment(comment_models.Comment):
    """
    The abstract superclass of all comments related to a delivery and feedback
    """
    feedback_set = models.ForeignKey('FeedbackSet')
    instant_publish = models.BooleanField(default=False)
    visible_for_students = models.BooleanField(default=False)

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
    group = models.ForeignKey(assignment_group.AssignmentGroup)
    points = models.PositiveIntegerField()
    published_by = models.ForeignKey(auth_models.User)
    created_datetime = models.DateTimeField(auto_now_add=True)
    published_datetime = models.DateTimeField(null=True, blank=True)
    deadline_datetime = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return u"{} - {}".format(self.group, self.deadline_datetime)


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
