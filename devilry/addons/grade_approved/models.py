from django.db import models
from django.utils.translation import ugettext as _
from devilry.core.gradeplugin import (GradeModel, GradeStats,
        GradeStatsDetail)


class AprGradeStats(GradeStats):
    column_headings = [_("Grade")]

    def __init__(self, assignmentgroups):
        self.details = []
        self.approvedcount = 0
        self.count = 0
        for group in assignmentgroups:
            delivery = group.get_latest_delivery_with_published_feedback()
            if delivery:
                grade = delivery.feedback.get_grade_as_short_string()
                gradeobj = delivery.feedback.grade
                if gradeobj.approved:
                    self.approvedcount += 1
            else:
                grade = "(%s)" % (group.get_localized_student_status())
            self.details.append(GradeStatsDetail(group, grade))
            self.count += 1

    def get_sums(self):
        return [self.get_short_sum()]

    def get_short_sum(self):
        return _("%(approvedcount)s of %(count)s approved" % dict(
            approvedcount = self.approvedcount,
            count = self.count))

    def iter_details(self):
        return self.details.__iter__()


class ApprovedGrade(GradeModel):
    approved = models.BooleanField(blank=True, default=False)

    @classmethod
    def gradestats(self, assignmentgroups):
        return AprGradeStats(assignmentgroups)

    def get_grade_as_short_string(self, feedback_obj):
        if self.approved:
            return _('Approved')
        else:
            return _('Not approved')

    def set_grade_from_xmlrpcstring(self, grade, feedback_obj):
        if grade in ('approved', '+'):
            self.approved = True
        elif grade in ('notapproved', '-'):
            self.approved = False
        else:
            raise ValueError(
                    'Invalid grade: "%s". Use "approved" or "+" to approve, ' \
                    'and "notapproved" or "-" to disapprove the delivery.' %
                    grade)

    def get_grade_as_xmlrpcstring(self, feedback_obj):
        if self.approved:
            return 'approved'
        else:
            return 'notapproved'
