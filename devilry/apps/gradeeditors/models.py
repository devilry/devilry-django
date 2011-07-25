from django.db import models
from django.contrib.auth.models import User

from devilry.apps.core.models import Delivery, Assignment


class Config(models.Model):
    """
    Stored by admins.
    """
    gradeeditorid = models.SlugField()
    assignment = models.OneToOneField(Assignment)
    config = models.TextField()


class FeedbackDraft(models.Model):
    """
    Stored by examiners.
    """
    delivery = models.ForeignKey(Delivery)
    saved_by = models.ForeignKey(User)
    shared = models.BooleanField()
    draft = models.TextField()

    class Meta:
        unique_together = ('delivery', 'saved_by')
