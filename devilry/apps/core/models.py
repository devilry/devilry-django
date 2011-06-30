"""
.. attribute:: pathsep

    Path separator used by node-paths. The value is ``'.'``, and it must not
    be changed.
"""


from datetime import datetime
import re

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, Max
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import ugettext as _
from django.utils.formats import date_format

from deliverystore import load_deliverystore_backend, FileNotFoundError
import gradeplugin



# TODO: indexes
# TODO: short_name ignorecase match on save.

pathsep = '.' # path separator for Node-paths


class AbstractIsAdmin(object):
    """ Abstract class implemented by all classes where it is natural to
    need to check if a user has admin rights. """

    @classmethod
    def q_is_admin(cls, user_obj):
        """
        Get a django.db.models.Q object matching all objects of this
        type where the given user is admin. The matched result is not
        guaranteed to contain unique items, so you should use distinct() on
        the queryset if this is required.

        This must be implemented in all subclassed.
        """
        raise NotImplementedError()

    @classmethod
    def where_is_admin(cls, user_obj):
        """ Get all objects of this type where the given user is admin. """
        return cls.objects.filter(cls.q_is_admin(user_obj)).distinct()

    @classmethod
    def where_is_admin_or_superadmin(cls, user_obj):
        """ Get all objects of this type where the given user is admin, or
        all objects if the user is superadmin. """
        if user_obj.is_superuser:
            return cls.objects.all()
        else:
            return cls.where_is_admin(user_obj)


class AbstractIsCandidate(object):

    # TODO: document this shit

    @classmethod
    def q_is_candidate(cls, user_obj):
        raise NotImplementedError()

    @classmethod
    def q_published(cls, old, active):
        raise NotImplementedError()

    @classmethod
    def where_is_candidate(cls, user_obj):
        return cls.objects.filter(
                cls.q_is_candidate(user_obj)
            ).distinct()

    @classmethod
    def published_where_is_candidate(cls, user_obj, old=True, active=True):
        return cls.objects.filter(
                cls.q_published(old=old, active=active) &
                cls.q_is_candidate(user_obj)
                ).distinct()

    @classmethod
    def active_where_is_candidate(cls, user_obj):
        return cls.published_where_is_candidate(user_obj, old=False, active=True)

    @classmethod
    def old_where_is_candidate(cls, user_obj):
        return cls.published_where_is_candidate(user_obj, active=False)


class AbstractIsExaminer(object):
    """ Abstract class implemented by all classes where it is natural to
    need to check if a user is examiner. """

    @classmethod
    def q_published(cls, old=True, active=True):
        """
        Return a django.models.Q object which matches all items of this type
        where :attr:`Assignment.publishing_time` is in the future.

        :param old: Include assignments where :attr:`Period.end_time`
            is in the past?
        :param active: Include assignments where :attr:`Period.end_time`
            is in the future?
        """
        raise NotImplementedError()


    @classmethod
    def q_is_examiner(cls, user_obj):
        """
        Return a django.models.Q object which matches items
        where the given user is examiner.
        """
        raise NotImplementedError()


    @classmethod
    def where_is_examiner(cls, user_obj):
        """ Get all items of this type where the given ``user_obj`` is
        examiner on one of the assignment groups.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return cls.objects.filter(
                cls.q_is_examiner(user_obj)
            ).distinct()

    @classmethod
    def published_where_is_examiner(cls, user_obj, old=True, active=True):
        """
        Get all published <assignment-classifications>` items of this type
        where the given ``user_obj`` is examiner on one of the assignment
        groups. Combines :meth:`q_is_examiner` and :meth:`q_published`.

        :param user_obj: :meth:`q_is_examiner`.
        :param old: :meth:`q_published`.
        :param active: :meth:`q_published`.
        :return: A django.db.models.query.QuerySet with duplicate
            assignments eliminated.
        """
        return cls.objects.filter(
                cls.q_published(old=old, active=active) &
                cls.q_is_examiner(user_obj)
                ).distinct()

    @classmethod
    def active_where_is_examiner(cls, user_obj):
        """
        Shortcut for :meth:`published_where_is_examiner` with
        ``old=False``.
        """
        return cls.published_where_is_examiner(user_obj, old=False,
                active=True)

    @classmethod
    def old_where_is_examiner(cls, user_obj):
        """
        Shortcut for :meth:`published_where_is_examiner` with
        ``active=False``.
        """
        return cls.published_where_is_examiner(user_obj, active=False)


class SaveInterface(object):
    def can_save(self, user_obj):
        """ Check if the give user has permission to save (or create) this
        node.

        A user can create a new node if it:

            - Is a superuser.
            - Is admin on any parentnode.

        A user can save if it:

            - Is a superuser.
            - Is admin on any parentnode.
            - Is admin on the node.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: bool
        """
        raise NotImplementedError()


def splitpath(path, expected_len=0):
    """ Split the path on :attr:`pathsep` and return the resulting list.
    Example:

    >>> splitpath('uio.ifi.matnat')
    ['uio', 'ifi', 'matnat']
    >>> splitpath('uio.ifi.matnat', expected_len=2)
    Traceback (most recent call last):
    ...
    ValueError: Path must have exactly 2 parts

    :param expected_len:
        Expected length of the resulting list. If the resulting list is not
        exactly the given length, ``ValueError`` is raised. If
        ``expected_len`` is 0 (default), no checking is done.
    """
    p = path.split(pathsep)
    if expected_len and len(p) != expected_len:
        raise ValueError('Path must have exactly %d parts' % expected_len)
    return p


class ShortNameField(models.SlugField):
    """ Short name field used by several of the core models.

    We have a hierarchy of objects with a short name, but they are not
    strictly equal (eg. we cannot use a superclass because Subject has a
    unique short_name).
    """
    patt = re.compile(r'^[a-z0-9_-]+$')
    def __init__(self, *args, **kwargs):
        kw = dict(
            max_length = 20,
            verbose_name = _('Short name'),
            db_index = True,
            help_text=_(
                "Max 20 characters. Only numbers, lowercase characters, '_' " \
                    "and '-'. " ))
        kw.update(kwargs)
        super(ShortNameField, self).__init__(*args, **kw)

    def validate(self, value, *args, **kwargs):
        super(ShortNameField, self).validate(value, *args, **kwargs)
        if not self.patt.match(value):
            raise ValidationError(_(
                "Can only contain numbers, lowercase letters, '_' and '-'. "))


class LongNameField(models.CharField):
    def __init__(self, *args, **kwargs):
        kw = dict(max_length=100,
            verbose_name='Long name',
            db_index = True,
            help_text=_(
                'A longer name, more descriptive than "Short name". '\
                'This is the name visible to students.'))
        kw.update(kwargs)
        super(LongNameField, self).__init__(*args, **kw)


class BaseNode(AbstractIsAdmin, SaveInterface):
    """
    The base class of the Devilry hierarchy. Implements basic functionality
    used by the other Node classes. This is an abstract datamodel, so it
    is never used directly.


    .. attribute:: short_name

        A django.db.models.SlugField_ with max 20 characters. Only numbers,
        letters, '_' and '-'.

    .. attribute:: long_name

        A django.db.models.CharField_ with max 100 characters. Gives a longer 
        description than :attr:`short_name`.
    """

    def __unicode__(self):
        return self.get_path()

    def get_path(self):
        return self.parentnode.get_path() + "." + self.short_name
    get_path.short_description = _('Path')
    
    def get_full_path(self):
        return self.parentnode.get_full_path() + "." + self.short_name
    get_full_path.short_description = _('Unique Path')
    
    def get_admins(self):
        """ Get a string with the username of all administrators on this node
        separated by comma and a space like: ``"uioadmin, superuser"``.
        
        Note that admins on parentnode(s) is not included.
        """
        return u', '.join([u.username for u in self.admins.all()])
    get_admins.short_description = _('Administrators')

    def is_admin(self, user_obj):
        """ Check if the given user is admin on this node or any parentnode.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: bool
        """
        try:
            self.admins.get(pk=user_obj.pk)
        except User.DoesNotExist, e:
            if self.parentnode:
                return self.parentnode.is_admin(user_obj)
        else:
            return True
        return False

    def _can_save_id_none(self, user_obj):
        """ Used by all except Node, which overrides. """
        return self.parentnode.is_admin(user_obj)

    def can_save(self, user_obj):
        if user_obj.is_superuser:
            return True
        if self.id == None:
            return self._can_save_id_none(user_obj)
        elif self.is_admin(user_obj):
            return True
        else:
            return False


class Node(models.Model, BaseNode):
    """
    This class is typically used to represent a hierarchy of institutions, 
    faculties and departments.


    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node, which
        is always a `Node`_.

    .. attribute:: admins

        A django.db.models.ManyToManyField_ that holds all the admins of the
        `Node`_.

    .. attribute:: child_nodes

        A set of child_nodes for this node
 
    .. attribute:: subjects

        A set of subjects for this node 
    """
    short_name = ShortNameField()
    long_name = LongNameField()
    parentnode = models.ForeignKey('self', blank=True, null=True, related_name='child_nodes')
    admins = models.ManyToManyField(User, blank=True)

    class Meta:
        verbose_name = _('Node')
        verbose_name_plural = _('Nodes')
        unique_together = ('short_name', 'parentnode')
        ordering = ['short_name']

    def _can_save_id_none(self, user_obj):
        if self.parentnode != None and self.parentnode.is_admin(user_obj):
            return True
        else:
            return False

    def get_path(self):
        if self.parentnode:
            return self.parentnode.get_path() + "." + self.short_name
        else:
            return self.short_name

    def get_full_path(self):
        return self.get_path()
    get_full_path.short_description = BaseNode.get_full_path.short_description
    
    def iter_childnodes(self):
        """
        Recursively iterates over all child nodes, and their child nodes.
        For a list of direct child nodes, use atribute child_nodes instead.
        """
        for node in Node.objects.filter(parentnode=self):
            yield node
            for c in node.iter_childnodes():
                yield c

    def clean(self, *args, **kwargs):
        """Validate the node, making sure it does not do something stupid.

        Always call this before save()! Read about validation here:
        http://docs.djangoproject.com/en/dev/ref/models/instances/#id1

        Raises ValidationError if:

            - The node is it's own parent.
            - The node is the child of itself or one of its childnodes.
        """
        if self.parentnode == self:
            raise ValidationError(_('A node can not be it\'s own parent.'))

        if self.short_name and self.parentnode == None:
            if self.id == None:
                if Node.objects.filter(short_name=self.short_name).count() > 0:
                    raise ValidationError(_('A node can not have the same '\
                        'short name as another within the same parent.'))


        for node in self.iter_childnodes():
            if node == self.parentnode:
                raise ValidationError(_('A node can not be the child of one of it\'s own children.'))

        super(Node, self).clean(*args, **kwargs)

    @classmethod
    def _get_nodepks_where_isadmin(cls, user_obj):
        """ Get a list with the primary key of all nodes where the given
        `user_obj` is admin. """
        admnodes = Node.objects.filter(admins=user_obj)
        l = []
        def add_admnodes(admnodes):
            for a in admnodes.all():
                l.append(a.pk)
                add_admnodes(a.child_nodes)
        add_admnodes(admnodes)
        return l

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(pk__in=cls._get_nodepks_where_isadmin(user_obj))

    @classmethod
    def get_by_path_kw(cls, pathlist):
        """ Used by :meth:`get_by_path` to create the required kwargs for
        Node.objects.get(). Might be a starting point for more sophisticated
        queries including paths. Example::

            ifi = Node.objects.get(**Node.get_by_path_kw(['uio', 'ifi']))

        :param pathlist: A list of node-names, like ``['uio', 'ifi']``.
        """
        kw = {}
        key = 'short_name'
        for short_name in reversed(pathlist):
            kw[key] = short_name
            key = 'parentnode__' + key
        return kw

    @classmethod
    def get_by_path(cls, path):
        """ Get a node by path.

        Raises :exc:`Node.DoesNotExist` if the query does not match.
        
        :param path: The path to a Node, like ``'uio.ifi'``.
        :type path: str
        :return: A Node-object.
        """
        return Node.objects.get(**Node.get_by_path_kw(path.split('.')))


class Subject(models.Model, BaseNode, AbstractIsExaminer, AbstractIsCandidate):
    """

    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node,
        which is always a `Node`_.

    .. attribute:: admins

        A django.db.models.ManyToManyField_ that holds all the admins of the
        `Node`_.

    .. attribute:: short_name

        A django.db.models.SlugField_ with max 20 characters. Only numbers,
        letters, '_' and '-'. Unlike all other children of
        :class:`BaseNode`, Subject.short_name is **unique**. This is mainly
        to avoid the overhead of having to recurse all the way to the top of
        the node hierarchy for every unique path.


    .. attribute:: periods

        A set of periods for this subject 
    """

    class Meta:
        verbose_name = _('Subject')
        verbose_name_plural = _('Subjects')
        ordering = ['short_name']

    short_name = ShortNameField(unique=True)
    long_name = LongNameField()
    parentnode = models.ForeignKey(Node, related_name='subjects')
    admins = models.ManyToManyField(User, blank=True)

    @classmethod
    def q_is_admin(cls, user_obj):
            return Q(admins__pk=user_obj.pk) \
                | Q(parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    @classmethod
    def get_by_path(self, path):
        """ Get a Subject by path.

        Only matches on :attr:`short_name` for subjects because it is
        guaranteed to be unique.

        Raises :exc:`Subject.DoesNotExist` if the query does not match.
        
        :param path: The :attr:`short_name` of a subject.
        :return: A Subject-object.
        """
        return Subject.objects.get(short_name=path)

    def get_path(self):
        """ Only returns :attr:`short_name` for subject since it is
        guaranteed to be unique. """
        return self.short_name

    def clean(self, *args, **kwargs):
        super(Subject, self).clean(*args, **kwargs)

    @classmethod
    def q_published(cls, old=True, active=True):
        now = datetime.now()
        q = Q(periods__assignments__publishing_time__lt=now)
        if not active:
            q &= ~Q(periods__end_time__gte=now)
        if not old:
            q &= ~Q(periods__end_time__lt=now)
        return q

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(periods__assignments__assignmentgroups__examiners=user_obj)

    @classmethod
    def q_is_candidate(cls, user_obj):
        return Q(periods__assignments__assignmentgroups__candidates=user_obj)


class Period(models.Model, BaseNode, AbstractIsExaminer, AbstractIsCandidate):
    """
    A Period represents a period of time, for example a half-year term
    at a university.


    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node,
        which is always a `Subject`_.

    .. attribute:: start_time

        A django.db.models.DateTimeField_ representing the starting time of
        the period.

    .. attribute:: end_time

        A django.db.models.DateTimeField_ representing the ending time of
        the period.

    .. attribute:: admins

        A django.db.models.ManyToManyField_ that holds all the admins of the
        node.

    .. attribute:: assignments

        A set of assignments for this period 
    """

    class Meta:
        verbose_name = _('Period')
        verbose_name_plural = _('Periods')
        unique_together = ('short_name', 'parentnode')
        ordering = ['short_name']

    short_name = ShortNameField()
    long_name = LongNameField()
    parentnode = models.ForeignKey(Subject, related_name='periods')
    start_time = models.DateTimeField(
            help_text=_(
                'Start time and end time defines when the period is active.'))
    end_time = models.DateTimeField(
            help_text=_(
                'Start time and end time defines when the period is active.'))
    admins = models.ManyToManyField(User, blank=True)
    minimum_points = models.PositiveIntegerField(default=0,
            help_text=_('Students must get at least this many points to '\
                    'pass the period.'))

    @classmethod
    def q_published(cls, old=True, active=True):
        now = datetime.now()
        q = Q(assignments__publishing_time__lt=now)
        if not active:
            q &= ~Q(end_time__gte=now)
        if not old:
            q &= ~Q(end_time__lt=now)
        return q

    @classmethod
    def q_is_candidate(cls, user_obj):
        return Q(assignmentgroups__candidates__student=user_obj)

    def student_sum_scaled_points(self, user):
        groups = AssignmentGroup.published_where_is_candidate(user).filter(
                parentnode__parentnode=self)
        return groups.aggregate(models.Sum('scaled_points'))['scaled_points__sum']

    def student_passes_period(self, user):
        groups = AssignmentGroup.published_where_is_candidate(user).filter(
                parentnode__parentnode=self,
                is_passing_grade=False,
                parentnode__must_pass=True)
        if groups.count() > 0:
            return False
        totalpoints = self.student_sum_scaled_points(user)
        return totalpoints >= self.minimum_points

    def get_must_pass_assignments(self):
        return self.assignments.filter(must_pass=True)

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(admins=user_obj) | \
                Q(parentnode__admins=user_obj) | \
                Q(parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    @classmethod
    def not_ended_where_is_admin(cls, user_obj):
        """ Returns a QuerySet matching all Periods where the given user is
        admin and end_time is in the future.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return cls.where_is_admin(user_obj).filter(end_time__gt=datetime.now())

    @classmethod
    def not_ended_where_is_admin_or_superadmin(cls, user_obj):
        """ Returns a QuerySet matching all Periods where the given user is
        admin or superadmin and end_time is in the future.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        if user_obj.is_superuser:
            return cls.objects.filter(end_time__gt=datetime.now())
        else:
            return cls.not_ended_where_is_admin(user_obj)

    @classmethod
    def get_by_path(self, path):
        """ Get a Period by path.

        Raises :exc:`Period.DoesNotExist` if the query does not match.
        Raises :exc:`ValueError` if the path does not contain exactly two
        path-elements (uses :func:`splitpath`).
        
        :param path: The path to a Period, like ``'inf1100.spring09'``.
        :return: A Period-object.
        """
        subject, period = splitpath(path, expected_len=2)
        return Period.objects.get(
                parentnode__short_name=subject,
                short_name=period)

    def clean(self, *args, **kwargs):
        """Validate the period.

        Always call this before save()! Read about validation here:
        http://docs.djangoproject.com/en/dev/ref/models/instances/#id1

        Raises ValidationError if start_time is after end_time.
        """
        if self.start_time and self.end_time:
            if self.start_time > self.end_time:
                raise ValidationError(_('Start time must be before end time.'))
        super(Period, self).clean(*args, **kwargs)

    def is_active(self):
        """ Returns true if the period is active
        """
        now = datetime.now()
        return self.start_time < now and self.end_time > now

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(assignments__assignmentgroups__examiners=user_obj)


class Assignment(models.Model, BaseNode, AbstractIsExaminer, AbstractIsCandidate):
    """

    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node,
        which is always a `Period`_.

    .. attribute:: publishing_time

        A django.db.models.DateTimeField_ representing the publishing time of
        the assignment.

    .. attribute:: anonymous

        A models.BooleanField specifying if the assignment should be
        anonymously for correcters.

    .. attribute:: admins

        A django.db.models.ManyToManyField_ that holds all the admins of the
        Node.

    .. attribute:: grade_plugin

        A django.db.models.CharField_ that holds the key of the current
        grade-plugin. More info on grade-plugins
        :ref:`here <grade-plugins>`.

    .. attribute:: assignmentgroups

        A set of the :class:`AssignmentGroup` for this assignment.

    .. attribute:: filenames
    
        A optional string of filenames separated by whitespace.

    .. attribute:: pointscale

        The points will be scaled down or up making the _this_
        number the maximum number of points. Defaults to 1.

    .. attribute:: autoscale
            
        If this field is True, the pointscale will automatically be set
        to the maximum number of points possible with the selected grade
        plugin.

    .. attribute:: maxpoints

        The maximum number of points possible without scaling. This is set by
        the grade plugin.

    .. attribute:: attempts

        The number of attempts a student get on this assignment. This is
        not a hard limit, but it makes the work of the examiners easier
        because the system will close groups (leaving students unable to
        deliver more attempts) when they have this many published
        feedbacks. Examiners can open closed groups, and they are
        notified when a group is automatically closed.

        If this is None, closing of groups has to be handled manually.

    .. attribute:: must_pass
        
        Each student must get a passing grade on this assignment to get a
        passing grade on the period. Defaults to False.


    .. attribute:: examiners_publish_feedbacks_directly

       Should feedbacks published by examiners be made avalable to the
       students immediately? If not, an administrator have to publish
       feedbacks. See also :attr:`Deadline.feedbacks_published`.
    """

    class Meta:
        verbose_name = _('Assignment')
        verbose_name_plural = _('Assignments')
        unique_together = ('short_name', 'parentnode')
        ordering = ['short_name']

    short_name = ShortNameField()
    long_name = LongNameField()
    parentnode = models.ForeignKey(Period, related_name='assignments')
    publishing_time = models.DateTimeField(
            verbose_name=_("Publishing time"))
    anonymous = models.BooleanField(default=False,
            verbose_name=_("Anonymous"))
    students_can_see_points = models.BooleanField(default=True,
            verbose_name=_("Students can see points"))
    admins = models.ManyToManyField(User, blank=True,
            verbose_name=_("Administrators"))
    grade_plugin = models.CharField(max_length=100,
            verbose_name=_("Grade plugin"),
            choices=gradeplugin.registry,
            default=gradeplugin.registry.getdefaultkey())
    filenames = models.TextField(blank=True, null=True,
            verbose_name=_("Filenames"),
            help_text=_('Filenames separated by newline or space. If '
                'filenames are used, students will not be able to deliver '
                'files where the filename is not among the given filenames.'))
    must_pass = models.BooleanField(default=False,
            verbose_name=_("Must pass"),
            help_text=_('Each student must get a passing grade on this ' \
                'assignment to get a passing grade on the period.'))
    pointscale = models.PositiveIntegerField(default=1,
            verbose_name = _("Scaled maximum points"),
            help_text=_(
                'The points will be scaled down or up making the _this_ '
                'number the maximum number of points on this assignment. '
                'You use this to adjust how much an assignment counts '
                'towards the final grade (or towards passing the period). '
                'A typical example is when you have one assignment where '
                'it is possible to get 30 points, and one assignment '
                'where it is possible to get 1 point (like '
                'with the approved/notapproved plugin). If you want both '
                'to count for maximum 40 points, you set this field to 40 '
                'on both assignments.'))
    maxpoints = models.PositiveIntegerField(default=0,
            help_text=_('The maximum number of points possible without '\
                'scaling.'))
    autoscale = models.BooleanField(default=True,
            verbose_name=_("Autoscale"),
            help_text=_('If this field is set, the pointscale will '\
                'automatically be set to the maximum number of points '\
                'possible with the selected grade plugin.'))
    attempts = models.PositiveIntegerField(default=None,
            verbose_name=_("Attempts"),
            null=True, blank=True,
            help_text=_('The number of attempts a student get on this '
                'assignment. This is not a hard limit, but it makes the '
                'work of the examiners easier because the system will ' 
                'close groups (leaving students unable to deliver more '
                'attempts) when they have this many published feedbacks. '
                'Examiners can open closed groups, and they are notified '
                'when a group is automatically closed. Leave this '
                'empty if you do not want to use this feature.'))
    examiners_publish_feedbacks_directly = models.BooleanField(default=True,
                                                     verbose_name=_("Examiners publish directly?"),
                                                     help_text=_('Should feedbacks published by examiners be made '
                                                                 'avalable to the students immediately? If not, an '
                                                                 'administrator have to publish feedbacks '
                                                                 'manually.'))

    @classmethod
    def q_published(cls, old=True, active=True):
        now = datetime.now()
        q = Q(publishing_time__lt=now)
        if not active:
            q &= ~Q(parentnode__end_time__gte=now)
        if not old:
            q &= ~Q(parentnode__end_time__lt=now)
        return q

    @classmethod
    def q_is_candidate(cls, user_obj):
        return Q(assignmentgroups__candidates__student=user_obj)

    def _update_scalepoints(self):
        for group in self.assignmentgroups.iterator():
            group.scaled_points = group._get_scaled_points()
            group.save()

    def save(self, *args, **kwargs):
        """ Save and recalculate the value of :attr:`maxpoints` and
        :attr:`pointscale`. """
        if self.autoscale:
            self.pointscale = self.maxpoints
        super(Assignment, self).save()
        self._update_scalepoints()

    def get_gradeplugin_registryitem(self):
        """ Get the :class:`devilry.core.gradeplugin.RegistryItem`
        for the current :attr:`grade_plugin`. """
        return gradeplugin.registry.getitem(self.grade_plugin)

    def get_filenames(self):
        """ Get the filenames as a list of strings. """
        return self.filenames.split()

    def validate_filenames(self, filenames):
        """ Raise ValueError unless each filename in the iterable
        ``filenames`` is one of the filenames on this assignment. Nothing is
        done if :attr:`filenames` is not set, or set to a empty string. """
        if self.filenames:
            valid = self.get_filenames()
            for filename in filenames:
                if not filename in valid:
                    raise ValueError(_("Invalid filename: %(filename)s" %
                        dict(filename=filename)))

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(admins=user_obj) | \
                Q(parentnode__admins=user_obj) | \
                Q(parentnode__parentnode__admins=user_obj) | \
                Q(parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(assignmentgroups__examiners=user_obj)

    @classmethod
    def get_by_path(self, path):
        """ Get a Assignment by path.

        Raises :exc:`Assignment.DoesNotExist` if the query does not match.
        Raises :exc:`ValueError` if the path does not contain exactly three
        path-elements (uses :func:`splitpath`).
        
        :param path:
            The path to a Assignment, like ``'inf1100.spring09.oblig1'``.
        :return: A Assignment-object.
        """
        subject, period, assignment = splitpath(path, expected_len=3)
        return Assignment.objects.get(
                parentnode__parentnode__short_name=subject,
                parentnode__short_name=period,
                short_name=assignment)

    def assignment_groups_where_is_examiner(self, user_obj):
        """ Get all assignment groups within this assignment where the given
        ``user_obj`` is examiner.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return self.assignmentgroups.filter(
            Q(examiners=user_obj))
    
    def assignment_groups_where_can_examine(self, user_obj):
        """ Get all assignment groups within this assignment where the given
        ``user_obj`` is examiner or admin. If the user is superadmin, all
        assignments are returned.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        if user_obj.is_superuser:
            return self.assignmentgroups.all()
        else:
            return self.assignmentgroups.filter(
                Q(examiners=user_obj) |
                Q(parentnode__admins=user_obj) |
                Q(parentnode__parentnode__admins=user_obj) |
                Q(parentnode__parentnode__parentnode__admins=user_obj) |
                Q(parentnode__parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj)))
            
    def clean(self, *args, **kwargs):
        """Validate the assignment.

        Always call this before save()! Read about validation here:
        http://docs.djangoproject.com/en/dev/ref/models/instances/#id1

        Raises ValidationError if ``publishing_time`` is not between
        :attr:`Period.start_time` and ``Period.end_time``.
        """
        super(Assignment, self).clean(*args, **kwargs)
        if self.publishing_time != None and self.parentnode != None:
            if self.publishing_time < self.parentnode.start_time  or \
                    self.publishing_time > self.parentnode.end_time:
                raise ValidationError(
                    _("Publishing time must be within it's period (%(period)s)."
                      % dict(period=unicode(self.parentnode))))


class Candidate(models.Model):
    """
    .. attribute:: assignment_group

        The :class:`AssignmentGroup` where this groups belongs.

    .. attribute:: student

        A student (a foreign key to a User).

    .. attribute:: candidate_id

        A optional candidate id. This can be anything as long as it is not
        more than 30 characters. When the assignment is anonymous, this is
        the "name" shown to examiners instead of the username of the
        student.
    """

    student = models.ForeignKey(User)
    assignment_group = models.ForeignKey('AssignmentGroup',
            related_name='candidates')

    # TODO unique within assignment as an option.
    candidate_id = models.CharField(max_length=30, blank=True, null=True)
    
    def get_identifier(self):
        """
        Gives the identifier of the candidate. When the Assignment is anyonymous
        the candidate_id is returned. Else, the student name is returned. This 
        method should always be used when retrieving the candidate identifier.
        """
        if self.assignment_group.parentnode.anonymous:
            if self.candidate_id == None or self.candidate_id.strip() == "":
                return _("candidate-id missing")
            else:
                return unicode(self.candidate_id)
        else:
            return unicode(self.student.username)

    
    def __unicode__(self):
        return self.get_identifier()

    def clean(self, *args, **kwargs):
        """Validate the assignment.

        Always call this before save()! Read about validation here:
        http://docs.djangoproject.com/en/dev/ref/models/instances/#id1

        Raises ValidationError if:

            - candidate id is empty on anonymous assignment.
        
        """
        if self.assignment_group.parentnode.anonymous:
            if not self.candidate_id:
                raise ValidationError(
                    _("Candidate id cannot be empty when assignment is anonymous.)"))
        
        super(Candidate, self).clean(*args, **kwargs)



# TODO: Constraint: cannot be examiner and student on the same assignmentgroup as an option.
class AssignmentGroup(models.Model, AbstractIsAdmin, AbstractIsExaminer):
    """
    Represents a student or a group of students. 


    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node,
        which is always an `Assignment`_.

    .. attribute:: name

        A optional name for the group.

    .. attribute:: candidates

        A django ``RelatedManager`` that holds the :class:`candidates
        <Candidate>` on this group.

    .. attribute:: examiners

        A django.db.models.ManyToManyField_ that holds the examiner(s) that are
        to correct and grade the assignment.

    .. attribute:: is_open

        A django.db.models.BooleanField_ that tells you if the group can add
        deliveries or not.

    .. attribute:: deliveries

        A set of deliveries for this assignmentgroup 

    .. attribute:: deadlines

        A set of deadlines for this assignmentgroup 

    .. attribute:: status

        **Cached field**: This status is a cached value of the status on the last
        deadline on this assignmentgroup.

    .. attribute:: status_mapping

        Maps :attr:`status` to a translated string for examiners and
        admins. ``status_mapping[0]`` contains a localized version of ``"No
        deliveries"``, and so on.

    .. attribute:: status_mapping_student

        Maps :attr:`status` to a translated string for students. The same as
        :attr:`status_mapping` except that ``status_mapping_student[2]``
        contains ``"Not corrected"``, and ``status_mapping_student[3]``
        contains ``"Corrected"``. This is because the student should never
        know about unpublished feedback.

    .. attribute:: points

        The number of points this group got on their latest published
        delivery. This fields is only updated when a published feedback
        is saved.

    .. attribute:: scaled_points

        The :attr:`points` of this group scaled according to
        :attr:`Assignment.pointscale` and :attr:`Assignment.maxpoints`.

        Calculated as: `float(pointscale)/maxpoints * points`.

        **Note:** This field is a cache for the calculation above.

    .. attribute:: NO_DELIVERIES

        The numberic value corresponding to :attr:`status` *no deliveries*.

    .. attribute:: DEADLINE_NOT_EXPIRED

        The numberic value corresponding to :attr:`status` *deadline not expired*.

    .. attribute:: AWAITING_CORRECTION

        The numberic value corresponding to :attr:`status` *awaiting correction*.

    .. attribute:: CORRECTED_NOT_PUBLISHED

        The numberic value corresponding to :attr:`status` *corrected, not published*.

    .. attribute:: CORRECTED_AND_PUBLISHED

        The numberic value corresponding to :attr:`status` *corrected and published*.

    """
    status_mapping = (
        _("No deliveries"),
        _("Has deliveries"),
        _("Corrected, not published"),
        _("Corrected and published"),
    )
    status_mapping_student = (
        status_mapping[0],
        status_mapping[1],
        status_mapping[1],
        _("Corrected"),
    )
    status_mapping_cssclass = (
        _("status_no_deliveries"),
        _("status_has_deliveries"),
        _("status_corrected_not_published"),
        _("status_corrected_and_published"),
    )
    status_mapping_student_cssclass = (
        status_mapping_cssclass[0],
        status_mapping_cssclass[1],
        status_mapping_cssclass[1],
        status_mapping_cssclass[3],
    )

    NO_DELIVERIES = 0
    HAS_DELIVERIES = 1
    CORRECTED_NOT_PUBLISHED = 2
    CORRECTED_AND_PUBLISHED = 3
    
    parentnode = models.ForeignKey(Assignment, related_name='assignmentgroups')
    name = models.CharField(max_length=30, blank=True, null=True)
    examiners = models.ManyToManyField(User, blank=True,
            related_name="examiners")
    is_open = models.BooleanField(blank=True, default=True,
            help_text = _('If this is checked, the group can add deliveries.'))
    status = models.PositiveIntegerField(
            default = 0,
            choices = enumerate(status_mapping),
            verbose_name = _('Status'))

    # Caches for fields in the last feedback
    points = models.PositiveIntegerField(default=0,
            help_text=_('Final number of points for this group. This '\
                'number is controlled by the grade plugin, and should not '\
                'be changed manually.'))
    scaled_points = models.FloatField(default=0.0)
    is_passing_grade = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']

    def _get_scaled_points(self):
        scale = float(self.parentnode.pointscale)
        maxpoints = self.parentnode.maxpoints
        if maxpoints == 0:
            return 0.0
        return (scale/maxpoints) * self.points

    def save(self, *args, **kwargs):
        create_default_deadline = False
        # Only if object doesn't yet exist in the database
        if not self.pk:
            create_default_deadline = True
        super(AssignmentGroup, self).save(*args, **kwargs)
        if create_default_deadline:
            self.create_default_deadline()

    def create_default_deadline(self):
        # Create the head deadline for this assignmentgroup
        head_deadline = Deadline()
        head_deadline.deadline = datetime.now()
        head_deadline.assignment_group = self
        head_deadline.is_head = True
        head_deadline.save()

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
        return Q(examiners=user_obj)

    def __unicode__(self):
        return u'%s (%s)' % (self.parentnode.get_path(),
                self.get_candidates())

    def get_students(self):
        """ Get a string containing all students in the group separated by
        comma and a space, like: ``superman, spiderman, batman``.

        **WARNING:** You should never use this method when the user is not
        an administrator. Use :meth:`get_candidates`
        instead.
        """
        return u', '.join(
                [c.student.username for c in self.candidates.all()])

    def get_candidates(self):
        """ Get a string containing all candiates in the group separated by
        comma and a space, like: ``superman, spiderman, batman`` for normal
        assignments, and something like: ``321, 1533, 111`` for anonymous
        assignments.
        """
        return u', '.join(
                [c.get_identifier() for c in self.candidates.all()])

    def get_examiners(self):
        """ Get a string contaning all examiners in the group separated by
        comma (``','``). """
        return u', '.join([u.username for u in self.examiners.all()])

    def is_admin(self, user_obj):
        return self.parentnode.is_admin(user_obj)

    def is_candidate(self, user_obj):
        return self.candidates.filter(student=user_obj).count() > 0

    def is_examiner(self, user_obj):
        """ Return True if user is examiner on this assignment group """
        return self.examiners.filter(pk=user_obj.pk).count() > 0

    def get_active_deadline(self):
        """ Get the active deadline.

        :return:
            Latest deadline, if no deadline has been created, the default deadline.
        """
        now = datetime.now()
        deadlines = self.deadlines.filter(deadline__gt=now).order_by('deadline')
        if len(deadlines) == 0:
            # Return the latest deadline (this will be the closest one in the 
            # past since the qry above failed)
            deadlines = self.deadlines.order_by('-deadline')
        return deadlines[0]

    def _get_status_from_qry(self):
        """Get status from active deadline"""
        active_deadline = self.get_active_deadline()
        return active_deadline.status

    def get_localized_status(self):
        """ Returns the current status string from :attr:`AssignmentGroup.status_mapping`. """
        return AssignmentGroup.status_mapping[self.status]

    def get_localized_student_status(self):
        """ Returns the current status string from
        :attr:`AssignmentGroup.status_mapping_student`. """
        return AssignmentGroup.status_mapping_student[self.status]

    def get_status_cssclass(self):
        """ Returns the current status string from
        :attr:`AssignmentGroup.status_mapping_cssclass`. """
        return AssignmentGroup.status_mapping_cssclass[self.status]

    def get_status_student_cssclass(self):
        """ Returns the current status string from
        :attr:`AssignmentGroup.status_mapping_student_cssclass`. """
        return AssignmentGroup.status_mapping_student_cssclass[self.status]

    def _update_status(self):
        """ Query for the correct status, and set :attr:`status`. """
        self.status = self._get_status_from_qry()

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



class Deadline(models.Model):
    """
    .. attribute:: assignment_group

        The assignment group where the deadline is registered.

    .. attribute:: deadline

        The deadline a DateTimeField.

    .. attribute:: text

        A optional deadline text.

   .. attribute:: deliveries

        A django ``RelatedManager`` that holds the :class:`deliveries
        <Delivery>` on this group.

   .. attribute:: status

        The status of this deadline. The data can be deduces from other data in the database, but
        since this requires complex queries, we store it as a integer
        instead, with the following values:

            0. No deliveries
            1. Has deliveries
            2. Corrected, not published
            3. Corrected and published

    .. attribute:: feedbacks_published

        If this boolean field is ``True``, the student can see all
        :class:`StaticFeedback` objects associated with this Deadline through a
        :class:`Delivery`. See also :attr:`Assignment.examiners_publish_feedbacks_directly`.
    """
    status = models.PositiveIntegerField(
            default = 0,
            choices = enumerate(AssignmentGroup.status_mapping),
            verbose_name = _('Status'))
    assignment_group = models.ForeignKey(AssignmentGroup,
            related_name='deadlines') 
    deadline = models.DateTimeField()
    text = models.TextField(blank=True, null=True)
    is_head = models.BooleanField(default=False)
    deliveries_available_before_deadline = models.BooleanField(default=False)
    feedbacks_published = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Deadline')
        verbose_name_plural = _('Deadlines')
        ordering = ['-deadline']

    def _get_status_from_qry(self):
        """Get status for active deadline"""
        if self.deliveries.all().count == 0:
            return AssignmentGroup.NO_DELIVERIES
        else:
            deliveries_with_feedback = [delivery for delivery in self.deliveries.all() \
                                        if delivery.feedbacks.all().count() > 0]
            if deliveries_with_feedback:
                if self.feedbacks_published:
                    return AssignmentGroup.CORRECTED_AND_PUBLISHED
                else:
                    return AssignmentGroup.CORRECTED_NOT_PUBLISHED
            else:
                return AssignmentGroup.HAS_DELIVERIES

    def _update_status(self):
        """ Query for the correct status, and set :attr:`status`. """
        self.status = self._get_status_from_qry()
    
    def clean(self, *args, **kwargs):
        """Validate the deadline.

        Always call this before save()! Read about validation here:
        http://docs.djangoproject.com/en/dev/ref/models/instances/#id1

        Raises ValidationError if:

            - ``deadline`` is before ``Assignment.publishing_time``. 
            - ``deadline`` is not before ``Period.end_time``.
        """
        if self.deadline != None:
            if self.deadline < self.assignment_group.parentnode.publishing_time:
                raise ValidationError(_('Deadline cannot be before publishing time.'))
            
            if self.deadline > self.assignment_group.parentnode.parentnode.end_time:
                raise ValidationError(
                    _("Deadline must be within it's period (%(period)s)."
                      % dict(period=unicode(self.assignment_group.parentnode.parentnode))))
        super(Deadline, self).clean(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.deadline)

    def is_old(self):
        """ Return True if :attr:`deadline` expired. """
        return self.deadline < datetime.now()

    def delete(self, *args, **kwargs):
        """ Prevent deletion if this is the head deadline """
        if self.is_head:
            raise PermissionDenied()
        super(Deadline, self).delete(*args, **kwargs)


# TODO: Constraint: Can only be delivered by a person in the assignment group?
#                   Or maybe an administrator?
class Delivery(models.Model, AbstractIsAdmin, AbstractIsCandidate, AbstractIsExaminer):
    """ A class representing a given delivery from an `AssignmentGroup`_.

    .. attribute:: assignment_group

        A django.db.models.ForeignKey_ pointing to the `AssignmentGroup`_
        that handed in the Delivery.

    .. attribute:: time_of_delivery

        A django.db.models.DateTimeField_ that holds the date and time the
        Delivery was uploaded.

    .. attribute:: deadline_tag

       Adjango.db.models.ForeignKey_ pointing to the Deadline for this Delivery.

    .. attribute:: number

        A django.db.models.PositiveIntegerField_ with the delivery-number
        within this assignment-group. This number is automatically
        incremented within each assignmentgroup, starting from 1. Must be
        unique within the assignment-group. Automatic incrementation is used
        if number is None when calling :meth:`save`.

    .. attribute:: delivered_by

        A django.db.models.ForeignKey_ pointing to the user that uploaded
        the Delivery

    .. attribute:: successful

        A django.db.models.BooleanField_ telling whether or not the Delivery
        was successfully uploaded.

    .. attribute:: after_deadline

        A django.db.models.BooleanField_ telling whether or not the Delivery
        was delived after deadline..

    .. attribute:: filemetas

        A set of filemetas for this delivery.

    .. attribute:: feedback

       A django.db.models.OneToOneField to StaticFeedback.

    """
    status_mapping = (
        _("Not corrected"),
        _("Corrected"),
        _("Corrected, not published"),
        _("Corrected and published"),
    )
    status_mapping_student = (
        status_mapping[0],
        status_mapping[1],
        status_mapping[2],
        status_mapping[3],
    )
    NOT_CORRECTED = 0
    CORRECTED = 1
    CORRECTED_AND_PUBLISHED = 2
    CORRECTED_NOT_PUBLISHED = 3

    # Fields automatically 
    time_of_delivery = models.DateTimeField()
    deadline_tag = models.ForeignKey(Deadline, related_name='deliveries')
    number = models.PositiveIntegerField()

    # Fields set by user
    assignment_group = models.ForeignKey(AssignmentGroup, related_name='deliveries')
    successful = models.BooleanField(blank=True, default=False)
    delivered_by = models.ForeignKey(User) # TODO: should be candidate!

    def delivered_too_late(self):
        """ Compares the deadline and time of delivery.
        If time_of_delivery is greater than the deadline, return True.
        """
        if self.deadline_tag.is_head:
            return False
        return self.time_of_delivery > self.deadline_tag.deadline
    after_deadline = property(delivered_too_late)

    class Meta:
        verbose_name = _('Delivery')
        verbose_name_plural = _('Deliveries')
        ordering = ['-time_of_delivery']
        unique_together = ('assignment_group', 'number')

    @classmethod
    def q_is_candidate(cls, user_obj):
        """
        Returns a django.models.Q object matching Deliveries where
        the given student is candidate.
        """
        return Q(assignment_group__candidates__student=user_obj)
    
    @classmethod
    def q_published(cls, old=True, active=True):
        now = datetime.now()
        q = Q(assignment_group__parentnode__publishing_time__lt = now)
        if not active:
            q &= ~Q(assignment_group__parentnode__parentnode__end_time__gte = now)
        if not old:
            q &= ~Q(assignment_group__parentnode__parentnode__end_time__lt = now)
        return q

    
    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(assignment_group__parentnode__admins=user_obj) | \
                Q(assignment_group__parentnode__parentnode__admins=user_obj) | \
                Q(assignment_group__parentnode__parentnode__parentnode__admins=user_obj) | \
                Q(assignment_group__parentnode__parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj)) \

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(assignment_group__examiners=user_obj)

    def add_file(self, filename, iterable_data):
        """ Add a file to the delivery.

        :param filename:
            A filename as defined in :class:`FileMeta`.
        :param iterable_data:
            A iterable yielding data that can be written to file using the
            write() method of a storage backend (byte strings).
        """
        filemeta = FileMeta()
        filemeta.delivery = self
        filemeta.filename = filename
        filemeta.size = 0
        filemeta.save()
        f = FileMeta.deliverystore.write_open(filemeta)
        filemeta.save()
        for data in iterable_data:
            f.write(data)
            filemeta.size += len(data)
        f.close()
        filemeta.save()
        return filemeta

    def get_feedback(self): # TODO: Rename to get_latest_feedback
        """ Get the feedback for this delivery. If the feedback does not
        exists, a new :class:`StaticFeedback`-object is created but not saved.

        :return:
            A :class:`StaticFeedback`-object with the delivery-attribute set
            to this delivery.
        """
        try:
            return self.feedbacks.order_by('-last_modified')[0]
        except IndexError:
            return StaticFeedback(delivery=self)

    def get_status_number(self):
        """ Get the numeric status for this delivery.

        :return: The numeric status:
            :attr:`Delivery.NOT_CORRECTED`,
            :attr:`Delivery.CORRECTED_NOT_PUBLISHED` or
            :attr:`Delivery.CORRECTED_AND_PUBLISHED`.
        """
        if self.feedbacks.all().count() > 0:
            return Delivery.CORRECTED_AND_PUBLISHED
        else:
            #return Delivery.CORRECTED_NOT_PUBLISHED # TODO: Handle the fact that this info does not exist anymore.
            return Delivery.NOT_CORRECTED
    
    def get_localized_status(self):
        """
        Returns the current status string from
        :attr:`AssignmentGroup.status_mapping`.
        """
        status = self.get_status_number()
        return status_mapping[status]

    def get_localized_student_status(self):
        """
        Returns the current status string from
        :attr:`status_mapping_student`.
        """
        status = self.get_status_number()
        return status_mapping_student[status]

    def get_status_cssclass(self):
        """ Returns the css class for the current status from
        :attr:`status_mapping_cssclass`. """
        return status_mapping_cssclass[self.get_status_number()]

    def get_status_student_cssclass(self):
        """ Returns the css class for the current status from
        :attr:`status_mapping_student_cssclass`. """
        return status_mapping_student_cssclass[
                self.get_status_number()]

    def _set_number(self):
        m = Delivery.objects.filter(assignment_group=self.assignment_group).aggregate(Max('number'))
        self.number = (m['number__max'] or 0) + 1

    def save(self, *args, **kwargs):
        """
        Set :attr:`number` automatically to one greater than what is was
        last.
        """
        self.time_of_delivery = datetime.now()
        if self.id == None:
            self.deadline_tag = self.assignment_group.deadlines.all().order_by('-deadline')[0]
            self._set_number()
        super(Delivery, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s - %s (%s)' % (self.assignment_group, self.number,
                date_format(self.time_of_delivery, "DATETIME_FORMAT"))


class StaticFeedback(models.Model, AbstractIsExaminer, AbstractIsCandidate):
    """ Represents a feedback for a `Delivery`_.

    Each delivery can have zero or more feedbacks. Each StaticFeedback object stores
    static data that an examiner has published on a delivery. StaticFeedback is
    created and edited in a _grade+feedback editor_ in a _grade plugin_, and
    when an examiner chose to publish feedback, a static copy of the data
    he/she created in the _grade+feedback editor_ is stored in a StaticFeedback.

    Feedbacks are only visible to students when
    :attr:`Deadline.feedbacks_published` on the related deadline is ``True``.
    Feedbacks are related to Deadlines through its :attr:`delivery`.

    Students are presented with the last feedback on a delivery, however they
    can browse every StaticFeedback on their deliveries. This history is to protect
    the student from administrators or examiners that change published
    feedback to avoid that a student can make an issue out of a bad feedback.

    .. attribute:: rendered_view

        The rendered HTML view.

    .. attribute:: saved_by

       The django.contrib.auth.models.User_ that created the StaticFeedback.

    .. attribute:: save_timestamp

       Date/time when this feedback was created.

    .. attribute:: delivery

       A django.db.models.ForeignKey_ that points to the `Delivery`_ where this feedback belongs.

    .. attribute:: grade

        The grade as a short string (max 12 chars).

    .. attribute:: points

        The number of points (integer).

    .. attribute:: is_passing_grade

        Boolean is passing grade?
    """
    delivery = models.ForeignKey(Delivery, related_name='feedbacks')
    rendered_view = models.TextField()
    grade = models.CharField(max_length=12)
    points = models.PositiveIntegerField(help_text = _('Number of points given on this feedback.'))
    is_passing_grade = models.BooleanField()
    save_timestamp = models.DateTimeField(auto_now=True, blank=False, null=False)
    saved_by = models.ForeignKey(User, blank=False, null=False)


    class Meta:
        verbose_name = _('Static feedback')
        verbose_name_plural = _('Static feedbacks')
        ordering = ['-save_timestamp']

    @classmethod
    def q_is_candidate(cls, user_obj):
        """
        Returns a django.models.Q object matching Deliveries where
        the given student is candidate.
        """
        return Q(delivery__assignment_group__candidates__student=user_obj)

    @classmethod
    def q_published(cls, old=True, active=True):
        now = datetime.now()
        q = Q(delivery__assignment_group__parentnode__publishing_time__lt = now)
        if not active:
            q &= ~Q(deliver__assignment_group__parentnode__parentnode__end_time__gte = now)
        if not old:
            q &= ~Q(delivery__assignment_group__parentnode__parentnode__end_time__lt = now)
        return q

    @classmethod
    def q_is_examiner(cls, user_obj):
        """
        Returns a django.models.Q object matching Feedbacks where
        the given student is candidate.
        """
        return Q(delivery__assignment_group__examiners=user_obj)

    def _publish_if_allowed(self):
        assignment = self.delivery.assignment_group.parentnode
        if assignment.examiners_publish_feedbacks_directly:
            deadline = self.delivery.deadline_tag
            deadline.feedbacks_published = True
            deadline.save()

    def save(self, *args, **kwargs):
        super(StaticFeedback, self).save(*args, **kwargs)
        self._publish_if_allowed()

    def __unicode__(self):
        return "StaticFeedback on %s" % self.delivery


class FileMeta(models.Model):
    """
    Represents the metadata for a file belonging to a `Delivery`_.

    .. attribute:: delivery

        A django.db.models.OneToOneField_ that points to the `Delivery`_ to
        be given feedback.

    .. attribute:: filename

        Name of the file.

    .. attribute:: size

        Size of the file in bytes.

    .. attribute:: deliverystore

        The current :ref:`DeliveryStore <devilry.apps.core.deliverystore>`.
    """
    delivery = models.ForeignKey(Delivery, related_name='filemetas')
    filename = models.CharField(max_length=255)
    size = models.IntegerField()

    deliverystore = load_deliverystore_backend()

    class Meta:
        verbose_name = _('FileMeta')
        verbose_name_plural = _('FileMetas')
        unique_together = ('delivery', 'filename')
        ordering = ['filename']

    def remove_file(self):
        """
        Remove the file using the
        :meth:`~devilry.core.deliverystore.DeliveryStoreInterface.remove`-method
        of the :attr:`deliverystore`.
        """
        return self.deliverystore.remove(self)

    def file_exists(self):
        """
        Check if the file exists using the
        :meth:`~devilry.core.deliverystore.DeliveryStoreInterface.exists`-method
        of the :attr:`deliverystore`.
        """
        return self.deliverystore.exists(self)

    def read_open(self):
        """
        Open file for reading using the
        :meth:`~devilry.core.deliverystore.DeliveryStoreInterface.read_open`-method
        of the :attr:`deliverystore`.
        """
        return self.deliverystore.read_open(self)

    def __unicode__(self):
        return self.filename


def filemeta_deleted_handler(sender, **kwargs):
    filemeta = kwargs['instance']
    try:
        filemeta.remove_file()
    except FileNotFoundError, e:
        # TODO: We should have some way of cleaning files which have no
        # corresponding FileMeta from DeliveryStores (could happen if the
        # disk is not mounted when this kicks in..
        pass

def feedback_grade_delete_handler(sender, **kwargs):
    feedback = kwargs['instance']
    if feedback.grade != None:
        feedback.grade.delete()

def feedback_update_assignmentgroup_status_handler(sender, **kwargs):
    feedback = kwargs['instance']
    update_deadline_and_assignmentgroup_status(feedback.delivery)

def delivery_update_assignmentgroup_status_handler(sender, **kwargs):
    delivery = kwargs['instance']
    update_deadline_and_assignmentgroup_status(delivery)

def update_deadline_and_assignmentgroup_status(delivery):
    delivery.deadline_tag._update_status()
    delivery.deadline_tag.save()
    delivery.assignment_group._update_status()
    delivery.assignment_group.save()

from django.db.models.signals import pre_delete, post_save
pre_delete.connect(filemeta_deleted_handler, sender=FileMeta)
pre_delete.connect(feedback_grade_delete_handler, sender=StaticFeedback)
post_save.connect(feedback_update_assignmentgroup_status_handler,
        sender=StaticFeedback)
post_save.connect(delivery_update_assignmentgroup_status_handler,
        sender=Delivery)
