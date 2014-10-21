from django.db import models
from django.contrib.auth.models import User

from devilry.apps.core.models import Assignment


# class DetectorAssignmentManager(models.Manager):


class DetectorAssignment(models.Model):
    """
    Tracks process of detector running on an assignment.

    An object of this model is created the first time detector
    processing is requested on an assignment. Subsequent processing
    requests re-use the same object.

    .. warning::
        This means that we do not allow parallel detector processing
        on the same assignment.
    """
    assignment = models.OneToOneField(Assignment)
    processing_started_datetime = models.DateTimeField(
        null=False, blank=False
    )
    processing_ended_datetime = models.DateTimeField(
        null=True, blank=True
    )
    processing_started_by = models.ForeignKey(User)


# class DetectorRelatedAssignment(models.Model):
#     detectorassignment = models.ForeignKey(DetectorAssignment)
#     relatedassignment = models.ForeignKey(Assignment)
