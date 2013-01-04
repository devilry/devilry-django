from django.db import models

from devilry.apps.core.models import RelatedStudent


class QualifiesForFinalExam(models.Model):
    student = models.OneToOneField(RelatedStudent)
    qualifies = models.BooleanField()