from django.db import models
from devilry_qualifiesforexam.models import Status
from devilry.apps.core.models import Assignment


class SelectedAssignmentSubset(models.Model):
    """
    Configuration for the ``devilry_qualifiesforexam_approved.subset``-plugin.
    """
    status = models.OneToOneField(Status, primary_key=True)


class SelectedAssignment(models.Model):
    subset = models.ForeignKey(SelectedAssignmentSubset)
    assignment = models.ForeignKey(Assignment)