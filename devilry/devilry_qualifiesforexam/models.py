# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from devilry.apps.core.models import RelatedStudent
from devilry.apps.core.models import Period
from devilry.devilry_account.models import User


class DeadlineTag(models.Model):
    timestamp = models.DateTimeField()
    tag = models.CharField(max_length=30, null=True, blank=True)


class PeriodTag(models.Model):
    period = models.OneToOneField(Period, primary_key=True)
    deadlinetag = models.ForeignKey(DeadlineTag)


class Status(models.Model):

    #: The list of qualified students are ready for export.
    #: Usually this means that all students have received a feedback
    #: on their assignments.
    READY = 'ready'

    #: Most students are ready for export.
    #: Almost all students have received a feedback on their assignments.
    #: TODO: Legacy, to be removed.
    ALMOSTREADY = 'almostready'

    #: Students have pending feedbacks.
    #: This should be used when students students are awaiting feedback on assignments.
    #: Typically the status is ``not ready`` if no students(or just a few) have received
    #: a feedback on the last assignment.
    NOTREADY = 'notready'

    #: Choice list for status on the qualification list.
    STATUS_CHOICES = [
        (READY, _('Ready for export')),
        (ALMOSTREADY, _('Most students are ready for export')),
        (NOTREADY, _('Not ready for export (retracted)')),
    ]

    #: The status of the qualification list.
    #: Note: The statuses does not represent any final state in the system, and
    #: the admin can use these statuses as they see fit
    status = models.CharField(
            max_length=30,
            blank=False,
            choices=STATUS_CHOICES)

    #: Period the qualifications are for.
    period = models.ForeignKey(Period, related_name='qualifiedforexams_status')

    #: Status created datetime. This is changed if the list updated.
    createtime = models.DateTimeField(auto_now_add=True)

    #: Message provided with the qualification list.
    #: Retracted message.
    message = models.TextField(blank=True, default='')

    #: The user that created the qualification list(an admin).
    user = models.ForeignKey(User)

    #: The plugin used.
    plugin = models.CharField(max_length=500, null=True, blank=True)

    #: The datetime when the list was exported.
    #: If this is null, this is considered a draft for preview before it's saved.
    exported_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-createtime']
        verbose_name = _('Qualified for final exam status')
        verbose_name_plural = _('Qualified for final exam statuses')

    def get_status_text(self):
        return self.STATUS_CHOICES_DICT[self.status]

    def clean(self):
        if self.status == 'notready' and not self.message:
            raise ValidationError('Message can not be empty when status is ``notready``.')
        if self.status != 'notready':
            if not self.plugin and not self.message:
                raise ValidationError('A ``message`` is required when no ``plugin`` is specified. '
                                      'The message should explain why a plugin is not used.')
        if self.status == 'notready':
            if self.plugin:
                raise ValidationError('``plugin`` is not allowed when status is ``notready``.')

    @classmethod
    def get_current_status(cls, period):
        latest = period.qualifiedforexams_status.all().order_by('-createtime')[:1]
        if len(latest) == 0:
            raise cls.DoesNotExist('The period with id={0} has no statuses'.format(period.id))
        return latest[0]

    def get_qualified_students(self):
        return self.students.filter(qualifies=True)

    def __unicode__(self):
        return u'Status(period={period}, id={id}, status={status})'.format(
            id=self.id, status=self.period, period=self.period)


class QualifiesForFinalExam(models.Model):
    #: The related :obj:`~.devilry.apps.core.RelatedStudent` the qualification is for.
    relatedstudent = models.ForeignKey(RelatedStudent)

    #: The related :obj:`~.Status` for this student.
    status = models.ForeignKey(Status, related_name='students')

    #: ``True`` if the student qualifies for the exam, else ``False``.
    qualifies = models.NullBooleanField()

    class Meta:
        unique_together = ('relatedstudent', 'status')

    def clean(self):
        if self.qualifies is None and self.status.status != 'almostready':
            raise ValidationError('Only the ``almostready`` status allows marking students as not ready for export.')
        if self.status.status == 'notready':
            raise ValidationError('Status ``notready`` does not allow marking qualified students.')

    def __unicode__(self):
        return u'{}-{}-{}'.format(self.relatedstudent, self.status, self.qualifies)
