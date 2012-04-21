from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from abstract_is_admin import AbstractIsAdmin
from node import Node

class Examiner(models.Model, AbstractIsAdmin):
    """
    .. attribute:: assignmentgroup

        The `AssignmentGroup`_ where this groups belongs.

    .. attribute:: user

        A foreign key to a User.
    """

    class Meta:
        app_label = 'core'
        unique_together = ('user', 'assignmentgroup')
        db_table = 'core_assignmentgroup_examiners'

    user = models.ForeignKey(User)
    assignmentgroup = models.ForeignKey('AssignmentGroup', related_name='examiners')

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(assignmentgroup__parentnode__admins=user_obj) | \
            Q(assignmentgroup__parentnode__parentnode__admins=user_obj) | \
            Q(assignmentgroup__parentnode__parentnode__parentnode__admins=user_obj) | \
            Q(assignmentgroup__parentnode__parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))
