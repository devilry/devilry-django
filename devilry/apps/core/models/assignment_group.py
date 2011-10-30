from datetime import datetime

from django.utils.translation import ugettext as _
from django.db.models import Q
from django.contrib.auth.models import User
from django.db import models

from node import Node
from abstract_is_admin import AbstractIsAdmin
from abstract_is_examiner import AbstractIsExaminer
from assignment import Assignment
from model_utils import Etag
from examiner import Examiner
import deliverytypes

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
                           help_text=_('An optional name for the group. Typically used a project '\
                                       'name on project assignments.'))
    #examiners = models.ManyToManyField(User, blank=True,
                                       #related_name="examiners", through=Examiner)
    is_open = models.BooleanField(blank=True, default=True,
            help_text = _('If this is checked, the group can add deliveries.'))
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


class AssignmentGroupTag(models.Model):
    """ An AssignmentGroup can be tagged with zero or more tags using this class. """
    assignment_group = models.ForeignKey(AssignmentGroup, related_name='tags')
    tag = models.SlugField(max_length=20, help_text='A tag can contain a-z, A-Z, 0-9 and "_".')

    class Meta:
        app_label = 'core'
        ordering = ['tag']
        unique_together = ('assignment_group', 'tag')
