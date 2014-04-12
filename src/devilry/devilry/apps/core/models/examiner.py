from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from abstract_is_admin import AbstractIsAdmin
from node import Node



class ExaminerManager(models.Manager):

    def bulkmake_examiner_for_groups(self, examineruser, *groups):
        """
        Make a user examiner for many groups.

        :param examineruser: A User object.
        :param groups: The groups where you want to add the examineruser as :class:`.Examiner`.

        .. warning::

            Always run this in a transaction. If an error occurs, you need to
            roll back the entire transaction, or handle that the examiner was
            added to only some of the groups.

        :return: ``None``. We do not perform a query to get the created examiners because
            we assume the most common scenario is to not do anything more with the examiners
            right after they have been created.
        """
        examiners_to_create = []
        for group in groups:
            examiner = Examiner(user=examineruser, assignmentgroup=group)
            examiners_to_create.append(examiner)
        self.bulk_create(examiners_to_create)





class Examiner(models.Model, AbstractIsAdmin):
    """
    .. attribute:: assignmentgroup

        The `AssignmentGroup`_ where this groups belongs.

    .. attribute:: user

        A foreign key to a User.
    """
    objects = ExaminerManager()

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
