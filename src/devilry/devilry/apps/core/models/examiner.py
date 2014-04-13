import random
import itertools

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from .abstract_is_admin import AbstractIsAdmin
from .node import Node
from .relateduser import RelatedExaminer
from .relateduser import RelatedStudent



class ExaminerManager(models.Manager):
    """
    Manager for :class:`.Examiner`.
    """
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

            Examiner.objects.bulkadd_examiners_to_groups(
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


    def bulkclear_examiners_from_groups(self, groups):
        """
        Clear examiners from the given groups.

        Examples::

            Examiner.objects.bulkclear_examiners_from_groups([group1, group2])
            Examiner.objects.bulkclear_examiners_from_groups(
                AssignmentGroup.objects.filter(parentnode=myassignment))

        :param groups:
            Iterable of :class:`devilry.apps.core.models.AssignmentGroup`
            objects to remove all current examiners from.

        .. seealso:: :meth:`.bulkremove_examiners_from_groups`.
        """
        Examiner.objects.filter(assignmentgroup__in=groups).delete()


    def bulkremove_examiners_from_groups(self, examinerusers, groups):
        """
        Remove the given examiners from the given groups.

        Examples::

            Examiner.objects.bulkremove_examiners_from_groups([user1, user2], [group1, group2])
            Examiner.objects.bulkremove_examiners_from_groups(
                [user1, user2],
                AssignmentGroup.objects.filter(parentnode=myassignment))

        :param examinerusers: An iterable of user objects.
        :param groups:
            Iterable of :class:`devilry.apps.core.models.AssignmentGroup`
            objects to remove all current examiners from.

        .. seealso:: :meth:`.bulkclear_examiners_from_groups`.
        """
        Examiner.objects.filter(user__in=examinerusers, assignmentgroup__in=groups).delete()



    def randomdistribute_examiners(self, examinerusers, groups):
        """
        Evenly randomdistribute the given examiners to the given groups.

        This method evenly distributes the ``examinerusers`` on the given ``groups``.   
        This means that at the number of groups assigned to each of the examiners  
        will differ by at most one.

        This is a fairly efficient method. It loops through all the groups 3 times,
        but two of those iterations is in C. It creates the :class:`.Examiner` objects
        using ``bulk_create()``.

        Examples::

            Examiner.objects.randomdistribute_examiners(
                examinerusers=[user1, user2],
                groups=[group1, group2, group3])
            Examiner.objects.randomdistribute_examiners(
                examinerusers=[user1, user2],
                groups=AssignmentGroup.objects.filter(parentnode=myassignment))


        :param examinerusers: An iterable of user objects.
        :param groups:
            Iterable of :class:`devilry.apps.core.models.AssignmentGroup`
            objects to remove all current examiners from.
        :return: ``None``. We do not perform a query to get the created examiners because
            we assume the most common scenario is to not do anything more with the examiners
            right after they have been created.

        .. note::

            You will usually want to call::

                Examiner.objects.bulkremove_examiners_from_groups(examinerusers, groups)

            before calling this method unless you KNOW that the ``examinerusers`` is
            not examiner on any of the ``groups``.

        :raises django.db.IntegrityError
            If any of the ``examinerusers`` is already examiner on any of the groups,
            the method will fail with IntegrityError, if we happen
            to random assign that examiner to a group where they are already
            examiner).
        """
        groups = [group for group in groups]
        examinerusers = [examiner for examiner in examinerusers]
        random.shuffle(groups)
        random.shuffle(examinerusers)
        examiners_to_create = []
        for examineruser in itertools.cycle(examinerusers):
            if groups:
                group = groups.pop()
                examiner = Examiner(user=examineruser, assignmentgroup=group)
                examiners_to_create.append(examiner)
            else:
                break                
        self.bulk_create(examiners_to_create)


    def setup_examiners_by_tags(self, period, examinerusers, groups):
        """
        Setup examiners by matching the :class:`.RelatedExaminer` tags of the given
        ``examinerusers`` with         the tags of the given groups.

        :param examinerusers: An iterable of user objects.
        :param groups:
            Iterable of :class:`devilry.apps.core.models.AssignmentGroup`
            objects to remove all current examiners from.
        :return: ``None``. We do not perform a query to get the created examiners because
            we assume the most common scenario is to not do anything more with the examiners
            right after they have been created.

        .. note::

            You will usually want to call::

                Examiner.objects.bulkremove_examiners_from_groups(examinerusers, groups)

            before calling this method unless you KNOW that the ``examinerusers`` is
            not examiner on any of the ``groups``.

        :raises django.db.IntegrityError
            If any of the ``examinerusers`` is already examiner on any of the
            groups they are assigned by tag.
        """
        from .assignment_group import AssignmentGroup

        # Group the AssignmentGroups and RelatedExaminers by tags
        groupids = [group.id for group in groups]
        groupsbytag = AssignmentGroup.objects.filter(id__in=groupids).group_by_tags()
        relatedexaminersbytag = period.relatedexaminers_by_tag(examinerusers)

        examiners_to_create = []
        groups_by_examiner = {}
        def add_examiner(examineruser, group):
            if not examineruser in groups_by_examiner:
                groups_by_examiner[examineruser] = set()
            if not group in groups_by_examiner[examineruser]:
                examiner = Examiner(user=relatedexaminer.user, assignmentgroup=group)
                examiners_to_create.append(examiner)
                groups_by_examiner[examineruser].add(group)

        # Loop through relatedexaminers grouped by tag
        for tag, relatedexaminers in relatedexaminersbytag.iteritems():
            # Loop through all groups matching the same tag as the current relatedexaminer
            for group in groupsbytag.get(tag, []):
                # Add all relatedexaminers with the current tag to the matched group
                for relatedexaminer in relatedexaminers:
                    add_examiner(relatedexaminer.user, group)
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
