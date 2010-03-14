from django.db import models
from django.utils.translation import ugettext as _
from devilry.core.models import Assignment, Delivery


class SchemaGrade(models.Model):
    assignment = models.OneToOneField(Assignment, primary_key=True)

class Entry(models.Model):
    schema = models.ForeignKey(SchemaGrade)
    text = models.TextField()
    max_points = models.IntegerField()

    def __unicode__(self):
        return self.text


class SchemaGradeResults(models.Model):
    def __unicode__(self):
        return unicode(self.result_set.count())
    

class Result(models.Model):
    results = models.ForeignKey(SchemaGradeResults)
    entry = models.ForeignKey(Entry)
    points = models.IntegerField()
