from django.db import models
from django.utils.translation import ugettext as _
from devilry.core.gradeplugin import GradeModel


class ApprovedGrade(GradeModel):
    approved = models.BooleanField(blank=True, default=False)

    def get_short_string(self, feedback_obj):
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
