from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from abstract_is_admin import AbstractIsAdmin
from node import Node



class ExaminerManager(models.Manager):
    # def bulkassign_groups_to_examiner(self, groups_grouped_by_examiner):
    #     """
    #     Bulkassign :class:`devirly.apps.core.models.AssignmentGroup` objects to examiner.

    #     This is typically used when setting up somewhat complex scenarios.
        
    #     :param groups_grouped_by_examiner:
    #         Dictionary where the key is a User-object, and the value is an iterable of group objects.

    #     Example::

    #         Examiner.objects.bulk_add_groups_to_examiner({
    #             examineruser1: [
    #                 group1, group2, group3
    #             ],
    #             examineruser2: [
    #                 group4, group5, group6
    #             ]
    #         })

    #     :return: ``None``. We do not perform a query to get the created examiners because
    #         we assume the most common scenario is to not do anything more with the examiners
    #         right after they have been created.
    #     """
        # examiners_to_create = []
        # for group, examiners_in_group in itertools.izip(groups, grouped_examiners):
        #     for examiner in examiners_in_group:
        #         examiner.assignment_group = group
        #         examiners_to_create.append(examiner)
        # self.bulk_create(examiners_to_create)


    def bulkadd_examiners_to_groups(self, examinerusers, groups):
        """
        Add one or more examiners to one or more groups. Perfect for adding
        examiners to groups when the user can select an unlimited number of groups
        and the examiners they want to add to the selected groups.

        If any of the ``examinerusers`` is already examiner on any of the groups,
        the method fails with :exc:`django.db.IntegrityError`.

        Example::

            Examiner.bulkadd_examiners_to_groups(
                examinerusers=[user1, user2],
                groups=[group1, group2, group3])

        :param examinerusers: An iterable of user objects.
        :param groups: An iterable of groups where you want to add the examineruser as :class:`.Examiner`.

        :return: ``None``. We do not perform a query to get the created examiners because
            we assume the most common scenario is to not do anything more with the examiners
            right after they have been created.

        .. warning::

            Always run this in a transaction. If an error occurs, you need to
            roll back the entire transaction, or handle that the examiner was
            added to only some of the groups.
        """
        examiners_to_create = []
        for group in groups:
            for examineruser in examinerusers:
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
