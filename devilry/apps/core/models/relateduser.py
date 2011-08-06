from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _
from django.db.models import Q

from period import Period
from node import Node
from abstract_is_admin import AbstractIsAdmin



class RelatedUserBase(models.Model, AbstractIsAdmin):
    username = models.SlugField(max_length=30, help_text=_('A username.'))

    class Meta:
        abstract = True # This model will then not be used to create any database table. Instead, when it is used as a base class for other models, its fields will be added to those of the child class.
        unique_together = ('period', 'username')
        app_label = 'core'

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(admins=user_obj) | \
                Q(period__admins=user_obj) | \
                Q(period__parentnode__admins=user_obj) | \
                Q(period__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    def __unicode__(self):
        return '{0}:{1}'.format(self.period, self.username)


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
