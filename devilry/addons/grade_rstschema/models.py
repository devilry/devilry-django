from django.db import models
from django.utils.translation import ugettext as _

from devilry.core.gradeplugin import GradeModel
from devilry.core.models import Assignment

from parser import rstdoc_from_string
import text
import field


class RstSchemaDefinition(models.Model):
    assignment = models.OneToOneField(Assignment, primary_key=True)
    schemadef = models.TextField()
    let_students_see_schema = models.BooleanField(default=False,
            help_text=_('Selecting this will let users see the ' \
                    'entire schema, instead of just the resulting grade.'))
    maxpoints = models.PositiveIntegerField(null=False, blank=True,
            default=0)

    def _parse_max_points(self):
        schemadef_document = rstdoc_from_string(self.schemadef)
        fields = field.extract_fields(schemadef_document)
        maxpoints = 0
        for f in fields:
            maxpoints += f.spec.get_max_points()
        return maxpoints

    def save(self, *args, **kwargs):
        self.maxpoints = self._parse_max_points()
        return super(RstSchemaDefinition, self).save(*args, **kwargs)

    def __unicode__(self):
        return "RstSchemaDefWidget(id:%s) for %s" % (self.pk,
                self.assignment)


def get_schemadef(feedback_obj):
    assignment = feedback_obj.get_assignment()
    return assignment.rstschemadefinition

def get_schemadef_document(feedback_obj):
    schemadef = get_schemadef(feedback_obj)
    schemadef_document = rstdoc_from_string(schemadef.schemadef)
    return schemadef_document


class RstSchemaGrade(GradeModel):
    schema = models.TextField()
    points = models.PositiveIntegerField(null=True, blank=True)

    @classmethod
    def get_autoscale(cls, assignment):
        return assignment.rstschemadefinition.maxpoints

    def _iter_points(self, feedback_obj):
        schemadef_document = get_schemadef_document(feedback_obj)
        fields = field.extract_fields(schemadef_document)
        values = text.extract_values(self.schema)
        for f, v in zip(fields, values):
            yield f.spec.get_points(v)

    def _parse_points(self):
        points = 0
        for p in self._iter_points(self.get_feedback_obj()):
            points += p
        return points

    def get_grade_as_short_string(self, feedback_obj):
        return "%d/%d" % (self.points,
                get_schemadef(feedback_obj).maxpoints)

    def set_grade_from_xmlrpcstring(self, grade, feedback_obj):
        schemadef_document = get_schemadef_document(feedback_obj)
        fields = field.extract_fields(schemadef_document)

        grade = text.strip_messages(grade)
        errors, output = text.validate_input(grade, fields)
        if errors > 0:
            raise ValueError('Fix the %s errors (marked with' \
                    'ERROR) in text below:\n\n%s' % (errors, output))
        self.schema = grade
        return output

    def get_grade_as_xmlrpcstring(self, feedback_obj):
        return self.schema

    #def get_grade_as_long_string(self, feedback_obj):
        #return self.schema

    #def supports_long_string(self):
        #return True

    def save(self, *args, **kwargs):
        feedback_obj = self.get_feedback_obj()
        self.points = self._parse_points()
        return super(RstSchemaGrade, self).save(*args, **kwargs)

    def get_points(self):
        return self.points

    def __unicode__(self):
        return "RstSchemaGrade(id:%s) for %s" % (self.id,
                self.get_feedback_obj())

