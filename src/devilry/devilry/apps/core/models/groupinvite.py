from datetime import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from .assignment_group import AssignmentGroup



class GroupInviteQuerySet(models.query.QuerySet):
    def filter_accepted(self):
        return self.filter(accepted=True)

    def filter_rejected(self):
        return self.filter(accepted=False)

    def filter_no_response(self):
        return self.filter(accepted=None)


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

    def filter_no_response(self):
        return self.get_queryset().filter_no_response()


class GroupInvite(models.Model):
    group = models.ForeignKey(AssignmentGroup)
    sent_datetime = models.DateTimeField(default=datetime.now)
    sent_by = models.ForeignKey(User, related_name='groupinvite_sent_by_set')
    sent_to = models.ForeignKey(User, related_name='groupinvite_sent_to_set')

    accepted = models.NullBooleanField(default=None)
    responded_datetime = models.DateTimeField(
        default=None, blank=True, null=True)

    objects = GroupInviteManager()

    class Meta:
        app_label = 'core'

    def clean(self):
        if self.accepted and not self.responded_datetime:
            self.responded_datetime = datetime.now()
        if self.sent_by and not self.group.candidates.filter(student=self.sent_by).exists():
            raise ValidationError('The user sending an invite must be a Candiate on the group.')
        if self.sent_to and self.group.candidates.filter(student=self.sent_to).exists():
            raise ValidationError(_(u'The student is already a member of the group.'))

        assignment = self.group.assignment
        if assignment.students_can_create_groups:
            if assignment.students_can_not_create_groups_after and assignment.students_can_not_create_groups_after < datetime.now():
                raise ValidationError(_('Creating project groups without administrator approval is not allowed on this assignment anymore. Please contact you course administrator if you think this is wrong.'))
        else:
            raise ValidationError(_('This assignment does not allow students to form project groups on their own.'))

        period = assignment.period
        if not period.relatedstudent_set.filter(user=self.sent_to).exists():
            raise ValidationError(_('The invited student is not registered on this subject.'))
