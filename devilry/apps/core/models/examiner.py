from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from abstract_is_admin import AbstractIsAdmin
from devilry.apps.core.models import RelatedExaminer
from devilry.devilry_account.models import User
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
        unique_together = ('relatedexaminer', 'assignmentgroup')
        db_table = 'core_assignmentgroup_examiners'

    #: Will be removed in 3.0 - see https://github.com/devilry/devilry-django/issues/812
    old_reference_not_in_use_user = models.ForeignKey(User, null=True, default=None, blank=True)

    #: The :class:`devilry.apps.core.models.assignment_group.AssignmentGroup`
    #: where this examiner belongs.
    assignmentgroup = models.ForeignKey('AssignmentGroup', related_name='examiners')

    #: ForeignKey to :class:`devilry.apps.core.models.relateduser.RelatedExaminer`
    #: (the model that ties User as examiner on a Period).
    relatedexaminer = models.ForeignKey(RelatedExaminer)

    @classmethod
    def q_is_admin(cls, user_obj):
        return \
            Q(assignmentgroup__parentnode__admins=user_obj) | \
            Q(assignmentgroup__parentnode__parentnode__admins=user_obj) | \
            Q(assignmentgroup__parentnode__parentnode__parentnode__admins=user_obj) | \
            Q(assignmentgroup__parentnode__parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(
                user_obj))

    def get_anonymous_name(self):
        """
        Get the anonymous name of this examiner.
        """
        return self.relatedexaminer.get_anonymous_name()

    def __unicode__(self):
        return u'Examiner {} for {}'.format(
            self.relatedexaminer, self.assignmentgroup
        )
