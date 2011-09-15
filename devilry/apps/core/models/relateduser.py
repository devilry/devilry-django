from django.db import models
from django.db.models import Q

from period import Period
from node import Node
from abstract_is_admin import AbstractIsAdmin



class RelatedUserBase(models.Model, AbstractIsAdmin):
    """
    Base class for :cls:`RelatedExaminer` and cls:`RelatedStudent`.

    This is used to generate AssignmentGroups and

    .. attribute:: username

        One or more usernames followed by optional tags. Format: usernameA, ...., usernameN (tag1, tag2, ..., tagN).
        For RelatedExaminer, only a single username is allowed.
    """
    username = models.CharField(max_length=200,
                                help_text='One or more usernames followed by optional tags. Format: usernameA, ...., usernameN (tag1, tag2, ..., tagN). For RelatedExaminer, only a single username is allowed.')

    class Meta:
        abstract = True # This model will then not be used to create any database table. Instead, when it is used as a base class for other models, its fields will be added to those of the child class.
        unique_together = ('period', 'username')
        app_label = 'core'

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(period__admins=user_obj) | \
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
                               help_text='The related period.')


class RelatedStudent(RelatedUserBase):
    """
    .. attribute:: period

        A django.db.models.ForeignKey_ that points to the `Period`_.
    """
    period = models.ForeignKey(Period, related_name='relatedstudents',
                               help_text='The related period.')
