from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from devilry.apps.core.models import RelatedStudent
from devilry.apps.core.models import Period


class DeadlineTag(models.Model):
    timestamp = models.DateTimeField()
    tag = models.CharField(max_length=30, null=True, blank=True)


class PeriodTag(models.Model):
    period = models.OneToOneField(Period, primary_key=True)
    deadlinetag = models.ForeignKey(DeadlineTag)


class Status(models.Model):
    READY, ALMOSTREADY, NOTREADY = ('ready', 'almostready', 'notready')
    STATUS_CHOICES = (
        (READY, _('Ready for export')),
        (ALMOSTREADY, _('Most students are ready for export')),
        (NOTREADY, _('Not ready for export (retracted)')),
    )
    STATUS_CHOICES_DICT = dict(STATUS_CHOICES)
    period = models.ForeignKey(Period, related_name='qualifiedforexams_status')
    status = models.SlugField(max_length=30, blank=False, choices=STATUS_CHOICES)
    createtime = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)
    user = models.ForeignKey(User)
    plugin = models.CharField(max_length=500, null=True, blank=True)
    exported_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-createtime']
        verbose_name = _('Qualified for final exam status')
        verbose_name_plural = _('Qualified for final exam statuses')

    def getStatusText(self):
        return self.STATUS_CHOICES_DICT[self.status]

    def clean(self):
        if not self.message:
            self.message = ''
        if isinstance(self.message, (str, unicode)) and self.message.strip() == '':
            self.message = ''
        if self.status == 'notready' and not self.message:
            raise ValidationError('Message can not be empty when status is ``notready``.')
        if self.status != 'notready':
            if not self.plugin and not self.message:
                raise ValidationError('A ``message`` is required when no ``plugin`` is specified. The message should explain why a plugin is not used.')
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
    relatedstudent = models.ForeignKey(RelatedStudent)
    status = models.ForeignKey(Status, related_name='students')
    qualifies = models.NullBooleanField()

    class Meta:
        unique_together = ('relatedstudent', 'status')

    def clean(self):
        if self.qualifies is None and self.status.status != 'almostready':
            raise ValidationError('Only the ``almostready`` status allows marking students as not ready for export.')
        if self.status.status == 'notready':
            raise ValidationError('Status ``notready`` does not allow marking qualified students.')
