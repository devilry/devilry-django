from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from devilry.apps.core.models import RelatedStudent
from devilry.apps.core.models import Period



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

    class Meta:
        ordering = ['-createtime']

    def getStatusText(self):
        return self.STATUS_CHOICES_DICT[self.status]


class QualifiesForFinalExam(models.Model):
    relatedstudent = models.ForeignKey(RelatedStudent)
    status = models.ForeignKey(Status,
        related_name='students')
    qualifies = models.NullBooleanField()

    class Meta:
        unique_together = ('relatedstudent', 'status')