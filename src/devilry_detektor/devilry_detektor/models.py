from django.db import models
from django.contrib.auth.models import User

from devilry.apps.core.models import Assignment


# class DetektorAssignmentManager(models.Manager):


class DetektorAssignment(models.Model):
    """
    Tracks process of detektor running on an assignment.

    An object of this model is created the first time detektor
    processing is requested on an assignment. Subsequent processing
    requests re-use the same object.

    .. warning::
        This means that we do not allow parallel detektor processing
        on the same assignment.
    """
    assignment = models.OneToOneField(Assignment)
    processing_started_datetime = models.DateTimeField(
        null=True, blank=True
    )
    processing_started_by = models.ForeignKey(
        User,
        null=True, blank=True)


# class DetektorRelatedAssignment(models.Model):
#     detektorassignment = models.ForeignKey(DetektorAssignment)
#     relatedassignment = models.ForeignKey(Assignment)
