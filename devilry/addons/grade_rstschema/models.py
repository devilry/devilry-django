from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType

from devilry.core.gradeplugin import GradeModel
from devilry.core.models import Assignment, Feedback, AssignmentGroup

from parser import rstdoc_from_string
import text
import field


class RstSchemaDefinition(models.Model):
    assignment = models.OneToOneField(Assignment, primary_key=True)
    schemadef = models.TextField()
    let_students_see_schema = models.BooleanField(default=False,
            help_text=_('Selecting this will let users see the ' \
                    'entire schema, instead of just the resulting grade.'))

def get_schemadef_document(feedback_obj):
    assignment = feedback_obj.get_assignment()
    schemadef = RstSchemaDefinition.objects.get(assignment=assignment)
    schemadef_document = rstdoc_from_string(schemadef.schemadef)
    return schemadef_document


class RstSchemaGrade(GradeModel):
    schema = models.TextField()
    points = models.PositiveIntegerField(null=True, blank=True)
    maxpoints = models.PositiveIntegerField(null=True, blank=True)

    @classmethod
    def calc_final_grade(self, period, gradeplugin_key, user):
        q = AssignmentGroup.published_where_is_candidate(user).filter(
                parentnode__parentnode=period,
                parentnode__grade_plugin=gradeplugin_key)
        if q.count() == 0:
            return None

        points = 0
        maxpoints = 0
        for group in q:
            delivery = group.get_latest_delivery_with_published_feedback()
            if delivery:
                grade = delivery.feedback.grade
                points += grade.points
                maxpoints += grade.maxpoints
        if maxpoints == 0:
            return None
        try:
            percent = (points * 100.0) / maxpoints
        except ZeroDivisionError:
            percent = 0.0
        finally:
            return "%.2f%% (%d/%d)" % (
                    percent, points, maxpoints)

    def iter_points(self, feedback_obj):
        schemadef_document = get_schemadef_document(feedback_obj)
        fields = field.extract_fields(schemadef_document)
        values = text.extract_values(self.schema)
        points = 0
        maxpoints = 0
        for f, v in zip(fields, values):
            yield f.spec.get_points(v), f.spec.get_max_points(v)

    def get_points(self, feedback_obj):
        points = 0
        maxpoints = 0
        for p, m in self.iter_points(feedback_obj):
            points += p
            maxpoints += m
        return points, maxpoints

    def get_percent(self):
        try:
            return (self.points * 100.0) / self.maxpoints
        except ZeroDivisionError:
            return 0.0
        
    def get_grade_as_short_string(self, feedback_obj):
        return "%.2f%% (%d/%d)" % (self.get_percent(), self.points,
                self.maxpoints)

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

    def save(self, *args, **kwargs):
        try:
            feedback_obj = self.get_feedback_obj()
        except Feedback.DoesNotExist:
            pass
        else:
            self.points, self.maxpoints = self.get_points(feedback_obj)
        return super(RstSchemaGrade, self).save(*args, **kwargs)

    def __unicode__(self):
        return "RstSchemaGrade(id:%s) for %s" % (self.id,
                self.get_feedback_obj())
