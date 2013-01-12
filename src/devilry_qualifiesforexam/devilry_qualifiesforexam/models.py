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
    STATUS_CHOICES = (
        ('ready', _('Ready for export')),
        ('almostready', _('Most students are ready for export')),
        ('notready', _('Not ready for export (retracted)')),
    )
    STATUS_CHOICES_DICT = dict(STATUS_CHOICES)
    period = models.ForeignKey(Period,
        related_name='qualifiedforexams_status')
    status = models.SlugField(max_length=30, blank=False, choices=STATUS_CHOICES)
    createtime = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)
    user = models.ForeignKey(User)
    plugin = models.CharField(max_length=500, null=True, blank=True)
    pluginsettings = models.TextField(null=True, blank=True)
    pluginsettings_summary = models.TextField(null=True, blank=True)
    exported_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-createtime']

    def getStatusText(self):
        return self.STATUS_CHOICES_DICT[self.status]

    def clean(self):
        if not self.message:
            self.message = ''
        if isinstance(self.message, (str, unicode)) and self.message.strip() == '':
            self.message = ''
        if self.status == 'notready' and not self.message:
            raise ValidationError('Message can not be empty when status is ``notready``.')
        if self.status != 'notready' and not self.plugin:
            raise ValidationError('``plugin`` is required for all statuses except ``notready``.')
        if self.status == 'notready':
            if self.plugin:
                raise ValidationError('``plugin`` is not allowed when status is ``notready``.')
            if self.pluginsettings:
                raise ValidationError('``pluginsettings`` is not allowed when status is ``notready``.')



class QualifiesForFinalExam(models.Model):
    relatedstudent = models.ForeignKey(RelatedStudent)
    status = models.ForeignKey(Status,
        related_name='students')
    qualifies = models.NullBooleanField()

    class Meta:
        unique_together = ('relatedstudent', 'status')

    def clean(self):
        if self.qualifies == None and self.status.status != 'almostready':
            raise ValidationError('Only the ``almostready`` status allows marking students as not ready for export.')
        if self.status.status == 'notready':
            raise ValidationError('Status ``notready`` does not allow marking qualified students.')
