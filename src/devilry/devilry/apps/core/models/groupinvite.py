from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from .assignment_group import AssignmentGroup



class GroupInviteQuerySet(models.query.QuerySet):
    def filter_accepted(self):
        return self.filter(accepted_datetime__isnull=False)


class GroupInviteManager(models.Manager):
    def get_queryset(self):
        return GroupInviteQuerySet(self.model, using=self._db)

    def filter(self, *args, **kwargs):
        return self.get_queryset().filter(*args, **kwargs)

    def all(self, *args, **kwargs):
        return self.get_queryset().filter(*args, **kwargs)

    def filter_accepted(self):
        return self.get_queryset().filter_accepted()

    def filter_rejected(self):
        return self.get_queryset().filter_rejected()


class GroupInvite(models.Model):
    group = models.ForeignKey(AssignmentGroup)
    sent_datetime = models.DateTimeField(default=datetime.now)
    sent_by = models.ForeignKey(User, related_name='groupinvite_sent_by_set')
    sent_to = models.ForeignKey(User, related_name='groupinvite_sent_to_set')
    accepted_datetime = models.DateTimeField(
        default=None, blank=True, null=True)
    rejected_datetime = models.DateTimeField(
        default=None, blank=True, null=True)

    objects = GroupInviteManager()

    class Meta:
        app_label = 'core'

    @property
    def accepted(self):
        return self.accepted_datetime != None

    @property
    def rejected(self):
        return self.rejected_datetime != None