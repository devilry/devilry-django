from datetime import datetime

from django.db.models import Q
from django.db import models

from node import Node
from abstract_is_admin import AbstractIsAdmin
from abstract_is_examiner import AbstractIsExaminer
from assignment import Assignment
from model_utils import Etag
import deliverytypes


class GroupPopValueError(ValueError):
    """
    Base class for exceptions raised by meth:`AssignmentGroup.pop_candidate`.
    """

class GroupPopToFewCandiatesError(GroupPopValueError):
    """
    Raised when meth:`AssignmentGroup.pop_candidate` is called on a group with
    1 or less candidates.
    """

class GroupPopNotCandiateError(GroupPopValueError):
    """
    Raised when meth:`AssignmentGroup.pop_candidate` is called with a candidate
    that is not on the group.
    """


# TODO: Constraint: cannot be examiner and student on the same assignmentgroup as an option.
class AssignmentGroup(models.Model, AbstractIsAdmin, AbstractIsExaminer, Etag):
    """
    Represents a student or a group of students. 

    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node,
        which is always an `Assignment`_.

    .. attribute:: name

        An optional name for the group.

    .. attribute:: candidates

        A django ``RelatedManager`` that holds the :class:`candidates <devilry.apps.core.models.Candidate>`
        on this group.

    .. attribute:: examiners

        A django.db.models.ManyToManyField_ that holds the examiner(s) that are
        to correct and grade the assignment.

    .. attribute:: is_open

        A django.db.models.BooleanField_ that tells you if the group can add
        deliveries or not.

    .. attribute:: deadlines

        A django ``RelatedManager`` that holds the :class:`deadlines <devilry.apps.core.models.Deadline>`
        on this group.

    .. attribute:: tags

        A django ``RelatedManager`` that holds the :class:`tags <devilry.apps.core.models.AssignmentGroupTag>`
        on this group.

    .. attribute:: feedback

       The last `StaticFeedback`_ (by save timestamp) on this assignmentgroup.

    .. attribute:: etag

       A DateTimeField containing the etag for this object.
    """

    parentnode = models.ForeignKey(Assignment, related_name='assignmentgroups')
    name = models.CharField(max_length=30, blank=True, null=True,
                           help_text='An optional name for the group. Typically used a project '\
                                       'name on project assignments.')
    is_open = models.BooleanField(blank=True, default=True,
            help_text = 'If this is checked, the group can add deliveries.')
    feedback = models.OneToOneField("StaticFeedback", blank=True, null=True)
    etag = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['id']

    def save(self, *args, **kwargs):
        create_dummy_deadline = False
        if self.id == None and self.parentnode.delivery_types == deliverytypes.NON_ELECTRONIC:
            create_dummy_deadline = True
        super(AssignmentGroup, self).save(*args, **kwargs)
        if create_dummy_deadline:
            self.deadlines.create(deadline=self.parentnode.parentnode.end_time)

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(parentnode__admins=user_obj) | \
                Q(parentnode__parentnode__admins=user_obj) | \
                Q(parentnode__parentnode__parentnode__admins=user_obj) | \
                Q(parentnode__parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    @classmethod
    def q_is_candidate(cls, user_obj):
        """
        Returns a django.models.Q object matching AssignmentGroups where
        the given student is candidate.
        """
        return Q(candidates__student=user_obj)

    @classmethod
    def where_is_candidate(cls, user_obj):
        """ Returns a QuerySet matching all AssignmentGroups where the
        given user is student.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return AssignmentGroup.objects.filter(cls.q_is_candidate(user_obj))

    @classmethod
    def published_where_is_candidate(cls, user_obj, old=True, active=True):
        """ Returns a QuerySet matching all :ref:`published
        <assignment-classifications>` assignment groups where the given user
        is student.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return AssignmentGroup.objects.filter(
                cls.q_is_candidate(user_obj) &
                cls.q_published(old=old, active=active))

    @classmethod
    def active_where_is_candidate(cls, user_obj):
        """ Returns a QuerySet matching all :ref:`active
        <assignment-classifications>` assignment groups where the given user
        is student.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return cls.published_where_is_candidate(user_obj, old=False)

    @classmethod
    def old_where_is_candidate(cls, user_obj):
        """ Returns a QuerySet matching all :ref:`old
        <assignment-classifications>` assignment groups where the given user
        is student.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return cls.published_where_is_candidate(user_obj, active=False)

    @classmethod
    def q_published(cls, old=True, active=True):
        now = datetime.now()
        q = Q(parentnode__publishing_time__lt = now)
        if not active:
            q &= ~Q(parentnode__parentnode__end_time__gte = now)
        if not old:
            q &= ~Q(parentnode__parentnode__end_time__lt = now)
        return q

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(examiners__user=user_obj)

    def __unicode__(self):
        return u'%s (%s)' % (self.parentnode.get_path(), self.get_candidates())

    def get_students(self):
        """ Get a string containing all students in the group separated by
        comma and a space, like: ``superman, spiderman, batman``.

        **WARNING:** You should never use this method when the user is not
        an administrator. Use :meth:`get_candidates`
        instead.
        """
        return u', '.join([c.student.username for c in self.candidates.all()])

    def get_candidates(self):
        """ Get a string containing all candiates in the group separated by
        comma and a space, like: ``superman, spiderman, batman`` for normal
        assignments, and something like: ``321, 1533, 111`` for anonymous
        assignments.
        """
        return u', '.join([c.identifier for c in self.candidates.all()])

    def get_examiners(self):
        """ Get a string contaning all examiners in the group separated by
        comma (``','``). """
        return u', '.join([examiner.user.username for examiner in self.examiners.all()])

    def is_admin(self, user_obj):
        return self.parentnode.is_admin(user_obj)

    def is_candidate(self, user_obj):
        return self.candidates.filter(student=user_obj).count() > 0

    def is_examiner(self, user_obj):
        """ Return True if user is examiner on this assignment group """
        return self.examiners.filter(user__id=user_obj.pk).count() > 0


    def can_delete(self, user_obj):
        """
        Check if the given user is permitted to delete this AssignmentGroup. A user is
        permitted to delete an object if the user is superadmin, or if the user
        is admin on the assignment (uses :meth:`.is_admin`). Only superusers
        are allowed to delete AssignmentGroups where :meth:`.is_empty` returns ``False``.

        :return: ``True`` if the user is permitted to delete this object.
        """
        if self.id == None:
            return False
        if user_obj.is_superuser:
            return True
        if self.parentnode != None and self.is_empty():
            return self.parentnode.is_admin(user_obj)
        else:
            return False

    def is_empty(self):
        """
        Returns ``True`` if this AssignmentGroup does not contain any deliveries.
        """
        from .delivery import Delivery
        return Delivery.objects.filter(deadline__assignment_group=self).count() == 0

    def get_active_deadline(self):
        """ Get the active :class:`Deadline`.

        This is always the last deadline on this group.

        :return:
            The latest deadline.
        """
        return self.deadlines.all().order_by('-deadline')[0]

    def can_save(self, user_obj):
        """ Check if the user has permission to save this AssignmentGroup. """
        if user_obj.is_superuser:
            return True
        elif self.parentnode:
            return self.parentnode.is_admin(user_obj)
        else:
            return False

    def can_add_deliveries(self):
        """ Returns true if a student can add deliveries on this assignmentgroup

        Both the assignmentgroups is_open attribute, and the periods start
        and end time is checked.
        """
        return self.is_open and self.parentnode.parentnode.is_active()

    def copy_all_except_candidates(self):
        """
        .. note:: Always run this is a transaction.
        """
        groupcopy = AssignmentGroup(parentnode=self.parentnode,
                                name=self.name,
                                is_open=self.is_open)
        groupcopy.full_clean()
        groupcopy.save()
        for tagobj in self.tags.all():
            groupcopy.tags.create(tag=tagobj.tag)
        for examiner in self.examiners.all():
            groupcopy.examiners.create(user=examiner.user)
        for deadline in self.deadlines.all():
            deadline.copy(groupcopy)
        groupcopy._set_latest_feedback_as_active()
        return groupcopy

    def pop_candidate(self, candidate):
        """
        Make a copy of this group using ``copy_all_except_candidates``, and
        add given candidate to the copied group and remove the candidate from
        this group.

        :param candidate: A :class:`devilry.apps.core.models.Candidate` object. The candidate must be among the candidates on this group.

        .. note:: Always run this is a transaction.
        """
        candidates = self.candidates.all()
        if len(candidates) < 2:
            raise GroupPopToFewCandiatesError('Can not pop caniddaites on a group with less than 2 candidates.')
        if not candidate in candidates:
            raise GroupPopNotCandiateError('The candidate to pop must be in the original group.')

        assignment = self.parentnode
        groupcopy = self.copy_all_except_candidates()
        candidate.assignment_group = groupcopy # Move the candidate to the new group
        candidate.full_clean()
        candidate.save()
        return groupcopy

    def recalculate_delivery_numbers(self):
        """
        Query all ``successful`` deliveries on this AssignmentGroup, ordered by
        ``time_of_delivery`` ascending, and number them with the oldest delivery
        as number 1.
        """
        from .delivery import Delivery
        qry = Delivery.objects.filter(deadline__assignment_group=self,
                                      successful=True)
        qry = qry.order_by('time_of_delivery')
        for number, delivery in enumerate(qry, 1):
            delivery.number = number
            delivery.save(autoset_number=False,
                          autoset_time_of_delivery=False)

    def _merge_examiners_into(self, target):
        target_examiners = set([e.user.id for e in target.examiners.all()])
        for examiner in self.examiners.all():
            if not examiner.user.id in target_examiners:
                examiner.assignmentgroup = target
                examiner.save()

    def _merge_candidates_into(self, target):
        target_candidates = set([e.student.id for e in target.candidates.all()])
        for candidate in self.candidates.all():
            if not candidate.student.id in target_candidates:
                candidate.assignment_group = target
                candidate.save()

    def _set_latest_feedback_as_active(self):
        from .static_feedback import StaticFeedback
        feedbacks = StaticFeedback.objects.filter(delivery__deadline__assignment_group=self)[:1]
        if len(feedbacks) == 1:
            latest_feedback = feedbacks[0]
            self.feedback = latest_feedback
            self.save()

    def merge_into(self, target):
        """
        Merge this AssignmentGroup into the ``target`` AssignmentGroup.
        Algorithm:

            - Copy in all candidates and examiners not already on the
              AssignmentGroup.
            - If ``target`` has no name, but this AssignmentGroup does,
              copy the name into target.
            - Delete all deliveries that are ``copy_of`` a delivery already in
              the target. We do this globally instead of for each deadline,
              since someone may have moved the deadline on one of the groups,
              but the delivery will still be the same.
            - Loop through all deadlines in this AssignmentGroup, and for each
              deadline:

              If the datetime and text of the deadline matches one already in
              ``target``, move the remaining deliveries into the target deadline.

              If the deadline and text does NOT match a deadline already in
              ``target``, change assignmentgroup of the deadline to the
              master group.
            - Recalculate delivery numbers of ``target`` using
              :meth:`recalculate_delivery_numbers`.
            - Set the latest feedback on ``target`` as the active feedback.
            - Run ``self.delete()``.

        .. note:: Always run this is a transaction.
        """
        from .deadline import Deadline
        from .delivery import Delivery
        Delivery.objects.filter(copy_of__deadline__assignment_group=target).delete()
        self._merge_examiners_into(target)
        self._merge_candidates_into(target)
        if not target.name:
            target.name = self.name
            target.save()
        for deadline in self.deadlines.all():
            try:
                matching_deadline = target.deadlines.get(deadline=deadline.deadline,
                                                         text=deadline.text)
                for delivery in deadline.deliveries.all():
                    delivery.deadline = matching_deadline
                    delivery.save(autoset_time_of_delivery=False,
                                  autoset_number=False)
            except Deadline.DoesNotExist:
                deadline.assignment_group = target
                deadline.save()
        target.recalculate_delivery_numbers()
        target._set_latest_feedback_as_active()
        self.delete()


class AssignmentGroupTag(models.Model):
    """
    An AssignmentGroup can be tagged with zero or more tags using this class.

    .. attribute:: assignment_group

        The `AssignmentGroup`_ where this groups belongs.

    .. attribute:: tag

        The tag. Max 20 characters. Can only contain a-z, A-Z, 0-9 and "_".
    """
    assignment_group = models.ForeignKey(AssignmentGroup, related_name='tags')
    tag = models.SlugField(max_length=20, help_text='A tag can contain a-z, A-Z, 0-9 and "_".')

    class Meta:
        app_label = 'core'
        ordering = ['tag']
        unique_together = ('assignment_group', 'tag')

    def __unicode__(self):
        return self.tag
