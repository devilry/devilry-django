from django.db import models
from django.utils.translation import ugettext as _


class ApprovedGrade(models.Model):
    approved = models.BooleanField(blank=True, default=False)

    def __unicode__(self):
        if self.approved:
            return _('Approved')
        else:
            return _('Not approved')

    def set_grade_from_string(self, grade):
        if grade in ('approved', '+'):
            self.approved = True
        elif grade in ('notapproved', '-'):
            self.approved = False
        else:
            raise ValueError(
                    'Invalid grade. Use "approved" or "+" to approve, ' \
                    'and "notapproved" or "-" to disapprove the delivery.')
