from django.db import models
from django.utils.translation import ugettext as _
from devilry.core.gradeplugin import GradeModel



class ApprovedGrade(GradeModel):
    approved = models.BooleanField(blank=True, default=False)

    @classmethod
    def get_maxpoints(cls, assignment):
        return 1

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

    def get_points(self):
        if self.approved:
            return 1
        else:
            return 0
