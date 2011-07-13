from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _

from period import Period



class RelatedUserBase(models.Model):
    """
    .. attribute:: tag

        A string with less than 50 characters.
    """
    tag = models.CharField(max_length=50, verbose_name=_('Tag'),
                          help_text=_('A string with less than 50 characters.'))
    user = models.ForeignKey(User, verbose_name=_('User'))

    class Meta:
        abstract = True # This model will then not be used to create any database table. Instead, when it is used as a base class for other models, its fields will be added to those of the child class.
        unique_together = ('tag', 'user')
        app_label = 'core'


class RelatedExaminer(RelatedUserBase):
    """
    .. attribute:: period

        A django.db.models.ForeignKey_ that points to the `Period`_.
    """
    period = models.ForeignKey(Period, related_name='relatedexaminers',
                               verbose_name=_('Period'))


class RelatedStudent(RelatedUserBase):
    """
    .. attribute:: period

        A django.db.models.ForeignKey_ that points to the `Period`_.
    """
    period = models.ForeignKey(Period, related_name='relatedstudents',
                               verbose_name=_('Period'))


    def __unicode__(self):
        return '{0}:{1}:{2}'.format(self.tag, self.user, self.period)
