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


    def setup_examiners_by_relatedusertags(self, period, examinerusers, groups):
        """
        TODO:
            Use RelatedExaminer tags, and match them with the current tags of the groups.
            This way, admins can change the tags of the groups and then apply examiners by tag.

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

        relatedexaminersbytag = period.relatedexaminers_by_tag()
        relatatedstudentsbytag = period.relatedstudents_by_tag()
        self.bulkclear_examiners_from_groups(groups)

        # Group AssignmentGroups by user to make direct lookup by user possible
        groupsbyuser = {}
        candidates = Candidate.objects.filter(assignmentgroup__in=groups)\
            .select_related('assignmentgroup', 'student')
        for candidate in candidates:
            if not candidate.student in groupsbyuser:
                groupsbyuser[candidate.student] = []
            groupsbyuser[candidate.student].append(candidate.group)

        examiners_to_create = []
        # Loop through relatedexaminers grouped by tag
        for tag, relatedexaminers in relatatedstudentsbytag.iteritems():
            # Loop through all relatedstudents matching the same tag as the current relatedexaminer
            for relatedstudent in relatatedstudentsbytag.get(tag, []):
                # Loop through all groups where the relatedstudent in candidate (usually 0 or 1)
                for group in groupsbyuser.get(relatedstudent.user, []):
                    # Add all relatedexaminers with the current tag to the matched group
                    for relatedexaminer in relatedexaminers:
                        examiner = Examiner(user=relatedexaminer.user, assignmentgroup=group)  
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
