from django.db import models
from django.utils.translation import ugettext as _

from devilry.core.gradeplugin import GradeModel
from devilry.core.models import Assignment



class RstSchemaDefinition(models.Model):
    assignment = models.OneToOneField(Assignment, primary_key=True)
    schemadef = models.TextField()
    let_students_see_schema = models.BooleanField(default=False,
            help_text=_('Selecting this will let users see the ' \
                    'entire schema, instead of just the resulting grade.'))

class RstSchemaGrade(GradeModel):
    schema = models.TextField()

    def get_grade_as_short_string(self, feedback_obj):
        return "TODO"

    def set_grade_from_xmlrpcstring(self, grade, feedback_obj):
        self.schema = grade

    def get_grade_as_xmlrpcstring(self, feedback_obj):
        return self.schema
