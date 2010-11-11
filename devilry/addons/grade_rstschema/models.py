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
    def get_maxpoints(cls, assignment=None):
        if assignment:
            return assignment.rstschemadefinition.maxpoints
        else:
            return 0

    @classmethod
    def init_example(cls, assignment, points):
        sd = RstSchemaDefinition()
        sd.assignment = assignment
        sd.let_students_see_schema = True
        sd.schemadef = """This is a schema. The schema author can write more
or less anything they want. They can make headings and organize questions if
needed.

A heading
#########

Is the assignment usable?

.. field:: no/yes
"""
        if points > 1:
            sd.schemadef += """
A subheading
============

Rate the overall quality:

.. field:: 0-%d
""" % (points - 1)
        sd.save()
        assignment.save() # update pointscale if autoscale

    @classmethod
    def get_example_xmlrpcstring(cls, assignment, points):
        """ This only works with schemas created by :meth:`init_example`. """
        schemadef = assignment.rstschemadefinition.schemadef
        f = text.examiner_format(schemadef)
        p = ["no", 0]
        if points > 1:
            p[0] = "yes"
            p[1] = points - 1
        return text.insert_values(f, p)

    def _iter_points(self, schemadef_document):
        fields = field.extract_fields(schemadef_document)
        values = text.extract_values(self.schema)
        for f, v in zip(fields, values):
            yield f.spec.get_points(v)

    def _parse_points(self, schemadef_document):
        points = 0
        for p in self._iter_points(schemadef_document):
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

    def save(self, feedback_obj, *args, **kwargs):
        schemadef_document = get_schemadef_document(feedback_obj)
        self.points = self._parse_points(schemadef_document)
        super(RstSchemaGrade, self).save(feedback_obj, *args, **kwargs)

    def get_points(self):
        return self.points

    def __unicode__(self):
        return "RstSchemaGrade(id:%s) for %s" % (self.id,
                self.get_feedback_obj())
