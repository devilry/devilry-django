from django.db import models
from django.contrib.auth.models import User

from devilry.apps.core.models import RelatedStudent
from devilry.apps.core.models import Period

class QualifiesForFinalExamPeriodStatus(models.Model):
    STATUS_CHOICES = (
        ('ready', 'Ready for export'),
        ('almostready', 'Most students are ready for export'),
        ('notready', 'Not ready'),
    )
    period = models.ForeignKey(Period)
    status = models.SlugField(max_length=30, blank=False)
    createtime = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)
    user = models.ForeignKey(User)
    plugin = models.CharField(max_length=500)
    pluginsettings = models.TextField(null=True, blank=True)


class QualifiesForFinalExam(models.Model):
    relatedstudent = models.OneToOneField(RelatedStudent)
    status = models.ForeignKey(QualifiesForFinalExamPeriodStatus,
        related_name='students')
    qualifies = models.BooleanField()
