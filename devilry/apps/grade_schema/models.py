from django.db import models
from ..core.models import Assignment
from ..core.gradeplugin import GradeModel


class SchemaGrade(models.Model):
    assignment = models.OneToOneField(Assignment, primary_key=True)

class Entry(models.Model):
    schema = models.ForeignKey(SchemaGrade)
    text = models.TextField()
    max_points = models.IntegerField()

    def __unicode__(self):
        return self.text


class SchemaGradeResults(GradeModel):
    def get_grade_as_short_string(self, feedback_obj):
        return unicode(self.result_set.count())
    

class Result(models.Model):
    results = models.ForeignKey(SchemaGradeResults)
    entry = models.ForeignKey(Entry)
    points = models.IntegerField()
