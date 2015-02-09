from django.db import models
from django.utils.translation import ugettext_lazy as _



class HelpLink(models.Model):
    help_url = models.URLField(max_length=500, unique=True)
    title = models.CharField(max_length=40, help_text=_('A title with no more than 40 characters.'))
    description = models.TextField(help_text=_('A longer description.'))
    superuser = models.BooleanField(help_text=_('Visible to superusers?'))
    nodeadmin = models.BooleanField(help_text=_('Visible to node admins?'))
    subjectadmin = models.BooleanField(help_text=_('Visible to subject admins?'))
    periodadmin = models.BooleanField(help_text=_('Visible to period admins?'))
    assignmentadmin = models.BooleanField(help_text=_('Visible to assignment admins?'))
    examiner = models.BooleanField(help_text=_('Visible to examiners?'))
    student = models.BooleanField(help_text=_('Visible to students?'))

    def __unicode__(self):
        return self.title
