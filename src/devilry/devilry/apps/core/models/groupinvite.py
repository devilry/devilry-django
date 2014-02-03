from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from .assignment_group import AssignmentGroup


class GroupInvite(models.Model):
    group = models.ForeignKey(AssignmentGroup)
    invite_sent_datetime = models.DateTimeField(default=datetime.now)
    sent_by = models.ForeignKey(User, related_name='groupinvite_sent_by_set')
    sent_to = models.ForeignKey(User, related_name='groupinvite_sent_to_set')
    accepted_datetime = models.DateTimeField(
        default=None, blank=True, null=True)
    rejected_datetime = models.DateTimeField(
        default=None, blank=True, null=True)

    class Meta:
        app_label = 'core'