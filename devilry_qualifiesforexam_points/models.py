from django.db import models
from devilry.devilry_qualifiesforexam.models import Status
from devilry.apps.core.models import Assignment


class PointsPluginSetting(models.Model):
    """
    Configuration for the ``devilry_qualifiesforexam_points``-plugin.
    """
    status = models.OneToOneField(Status, primary_key=True,
        related_name="%(app_label)s_%(class)s")
    minimum_points = models.PositiveIntegerField()


class PointsPluginSelectedAssignment(models.Model):
    subset = models.ForeignKey(PointsPluginSetting)
    assignment = models.ForeignKey(Assignment)
