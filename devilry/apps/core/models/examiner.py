from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

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

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    assignmentgroup = models.ForeignKey('AssignmentGroup', related_name='examiners')
    automatic_anonymous_id = models.CharField(
        max_length=255, blank=True, null=False, default='',
        help_text='An automatically generated anonymous ID.')

    @classmethod
    def q_is_admin(cls, user_obj):
        return \
            Q(assignmentgroup__parentnode__admins=user_obj) | \
            Q(assignmentgroup__parentnode__parentnode__admins=user_obj) | \
            Q(assignmentgroup__parentnode__parentnode__parentnode__admins=user_obj) | \
            Q(assignmentgroup__parentnode__parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(
                user_obj))

    def get_anonymous_displayname(self):
        return self.automatic_anonymous_id or _('Anonymous ID missing')
