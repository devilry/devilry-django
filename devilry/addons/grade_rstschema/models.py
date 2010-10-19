from django.db import models
from django.utils.translation import ugettext as _

from devilry.core.gradeplugin import (GradeModel, get_registry_key,
        GradeStats, GradeStatsDetail)
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
    autoscale = models.BooleanField(blank=True, default=True)
    scale = models.PositiveIntegerField(null=True, blank=True)
    percent = models.FloatField(null=True, blank=True)

    @classmethod
    def recalculate_percents(cls, period):
        gradeplugin_key = get_registry_key(RstSchemaGrade)
        schemadefs = []
        for assignment in period.assignments.filter(
                grade_plugin=gradeplugin_key):
            try:
                schemadef = assignment.rstschemadefinition
            except RstSchemaDefinition.DoesNotExist:
                pass
            else:
                schemadefs.append(schemadef)
        scalesum = 0
        for schemadef in schemadefs:
            schemadef.set_scale()
            scalesum += schemadef.scale
        for schemadef in schemadefs:
            schemadef.percent = (schemadef.scale*100.0) / scalesum
            schemadef.save()

    def get_max_points(self):
        schemadef_document = rstdoc_from_string(self.schemadef)
        fields = field.extract_fields(schemadef_document)
        maxpoints = 0
        for f in fields:
            maxpoints += f.spec.get_max_points()
        return maxpoints

    def set_scale(self):
        if self.autoscale:
            self.scale = self.get_max_points()
        elif self.scale == None:
            self.scale = self.get_max_points()

    def save(self, *args, **kwargs):
        self.set_scale()
        ret = super(RstSchemaDefinition, self).save(*args, **kwargs)



def get_schemadef(feedback_obj):
    assignment = feedback_obj.get_assignment()
    return RstSchemaDefinition.objects.get(assignment=assignment)

def get_schemadef_document(feedback_obj):
    schemadef = get_schemadef(feedback_obj)
    schemadef_document = rstdoc_from_string(schemadef.schemadef)
    return schemadef_document



class RstGradeStats(GradeStats):
    column_headings = (_("Points"), _("Percent of total"), _("Grade"))

    helptext = _(
            '"Percent of total" is how much a assignment counts ' \
            'towards the "sum". This percent might not be correct before ' \
            'all the assignments has been corrected.')

    def __init__(self, assignmentgroups):
        self.final_grade = None
        self.details = []
        scaledpoints = 0
        scaledmaxpoints = 0
        for group in assignmentgroups:
            schemadef = group.parentnode.rstschemadefinition
            scaledmaxpoints += schemadef.scale
            percent = "%.2f%%" % schemadef.percent

            delivery = group.get_latest_delivery_with_published_feedback()
            if delivery:
                gradeobj = delivery.feedback.grade
                p = gradeobj.get_scaled_points(schemadef.scale)
                scaledpoints += p
                points = "%d/%d" % (gradeobj.points, gradeobj.maxpoints)
                grade = "%.2f/%s" % (p, schemadef.scale)
            else:
                points = ''
                grade = "0/%d (%s)" % (schemadef.scale,
                        group.get_localized_student_status())

            self.details.append(GradeStatsDetail(group,
                points, percent, grade))
        if scaledmaxpoints != 0:
            try:
                percent = (scaledpoints * 100.0) / scaledmaxpoints
            except ZeroDivisionError:
                percent = 0.0
            finally:
                self.final_grade = "%.2f/%d (%.2f%%)" % (
                        scaledpoints, scaledmaxpoints, percent)

    def get_sums(self):
        return ('', '', self.final_grade)

    def get_short_sum(self):
        return self.final_grade

    def iter_details(self):
        return self.details.__iter__()



class RstSchemaGrade(GradeModel):
    schema = models.TextField()
    points = models.PositiveIntegerField(null=True, blank=True)
    maxpoints = models.PositiveIntegerField(null=True, blank=True)

    @classmethod
    def gradestats(self, assignmentgroups):
        return RstGradeStats(assignmentgroups)

    def get_scaled_points(self, scale):
        scalepercent = float(scale) / self.maxpoints
        return self.points * scalepercent

    def iter_points(self, feedback_obj):
        schemadef_document = get_schemadef_document(feedback_obj)
        fields = field.extract_fields(schemadef_document)
        values = text.extract_values(self.schema)
        for f, v in zip(fields, values):
            yield f.spec.get_points(v), f.spec.get_max_points()

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
        return "%d/%d" % (self.points,
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

