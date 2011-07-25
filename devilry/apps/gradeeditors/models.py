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
    draft = models.TextField()
    save_timestamp = models.DateTimeField(auto_now=True, blank=False, null=False,
                                          help_text='Time when this feedback was saved. Since FeedbackDraft '
                                                    'is immutable, this never changes.')
    saved_by = models.ForeignKey(User)
