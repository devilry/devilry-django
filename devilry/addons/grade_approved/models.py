from django.db import models
from django.utils.translation import ugettext as _


class ApprovedGrade(models.Model):
    approved = models.BooleanField(blank=True, default=False)

    def __unicode__(self):
        if self.approved:
            return _('Approved')
        else:
            return _('Not approved')
