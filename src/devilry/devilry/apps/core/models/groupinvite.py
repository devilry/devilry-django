from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from .assignment_group import AssignmentGroup


class GroupInvite(models.Model):
    group = models.ForeignKey(AssignmentGroup)
    invite_sent_datetime = models.DatetimeField(default=datetime.now)
    sent_to = models.ForeignKey(User)
    accepted_datetime = models.DatetimeField(
        default=None, blank=True, null=True)
    rejected_datetime = models.DatetimeField(
        default=None, blank=True, null=True)

    class Meta:
        app_label = 'core'