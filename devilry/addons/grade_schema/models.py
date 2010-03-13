from django.db import models
from django.utils.translation import ugettext as _
from devilry.core.models import Assignment, Delivery


class SchemaGrade(models.Model):
    assignment = models.OneToOneField(Assignment, primary_key=True)

    def __unicode__(self):
        return unicode(self.entry_set.count())

class Entry(models.Model):
    schema = models.ForeignKey(SchemaGrade)
    text = models.TextField()
    max_points = models.IntegerField()

    def __unicode__(self):
        return self.text

class SchemaGradeResult(models.Model):
    entry = models.ForeignKey(Entry)
    delivery = models.OneToOneField(Delivery)
    points = models.IntegerField()
