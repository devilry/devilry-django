from django.db import models

from devilry.core.gradeplugin import GradeModel
from devilry.core.models import Assignment


class RstSchemaDefinition(models.Model):
    assignment = models.OneToOneField(Assignment, primary_key=True)
    schema = models.TextField()


class RstSchemaGrade(GradeModel):
    schema = models.TextField()

    def get_short_string(self):
        return "TODO"

    def set_grade_from_xmlrpcstring(self, grade):
        self.schema = grade

    def get_grade_as_xmlrpcstring(self):
        return self.schema
