"""
.. attribute:: pathsep

    Path separator used by node-paths. The value is ``'.'``, and it must not
    be changed.
"""


from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, Max
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from deliverystore import load_deliverystore_backend, FileNotFoundError
import gradeplugin



# TODO: indexes
# TODO: Complete/extend and document CommonInterface.
# TODO: short_name ignorecase match on save.

pathsep = '.' # path separator for Node-paths


class CommonInterface(object):

    @classmethod
    def where_is_admin(cls, user_obj):
        """ Get all objects of this type where the given user is admin. """
        raise NotImplementedError()

    @classmethod
    def where_is_admin_or_superadmin(cls, user_obj):
        """ Get all objects of this type where the given user is admin, or
        all objects if the user is superadmin. """
        if user_obj.is_superuser:
            return cls.objects.all()
        else:
            return cls.where_is_admin(user_obj)

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
    def __init__(self, *args, **kwargs):
        kw = dict(
            max_length = 20,
            verbose_name = _('Short name'),
            db_index = True,
            help_text=_(
                "Max 20 characters. Only numbers, letters, '_' and '-'. "\
                "Only visible to examiners and admins."))
        kw.update(kwargs)
        super(ShortNameField, self).__init__(*args, **kw)


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


class BaseNode(CommonInterface):
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

    .. attribute:: nodes

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

    def _can_save_id_none(self, user_obj):
        if self.parentnode == None and not user_obj.is_superuser:
            return False
        else:
            return True

    def get_path(self):
        if self.parentnode:
            return self.parentnode.get_path() + "." + self.short_name
        else:
            return self.short_name

    def get_full_path(self):
        return self.get_path()
    get_full_path.short_description = BaseNode.get_full_path.short_description
    
    def iter_childnodes(self):
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
    def where_is_admin(cls, user_obj):
        """ Returns a QuerySet matching all Nodes where the given user is
        admin.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return Node.objects.filter(pk__in=cls._get_nodepks_where_isadmin(user_obj))

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


class Subject(models.Model, BaseNode):
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

    short_name = ShortNameField(unique=True)
    long_name = LongNameField()
    parentnode = models.ForeignKey(Node, related_name='subjects')
    admins = models.ManyToManyField(User, blank=True)
    
    @classmethod
    def where_is_admin(cls, user_obj):
        """ Returns a QuerySet matching all Subjects where the given user is
        admin.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return Subject.objects.filter(
                Q(admins__pk=user_obj.pk)
                | Q(parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))).distinct()

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


class Period(models.Model, BaseNode):
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

    @classmethod
    def where_is_admin(cls, user_obj):
        """ Returns a QuerySet matching all Periods where the given user is
        admin.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return Period.objects.filter(
                Q(admins=user_obj) |
                Q(parentnode__admins=user_obj) |
                Q(parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))
        ).distinct()

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

class Assignment(models.Model, BaseNode):
    """

    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node,
        which is always a `Period`_.

    .. attribute:: publishing_time

        A django.db.models.DateTimeField_ representing the publishing time of
        the assignment.

    .. attribute:: deadline

        A django.db.models.DateTimeField_ representing the deadline of the
        assignment.

    .. attribute:: admins

        A django.db.models.ManyToManyField_ that holds all the admins of the
        Node.

    .. attribute:: grade_plugin

        A django.db.models.CharField_ that holds the key of the current
        grade-plugin. More info on grade-plugins
        :ref:`here <grade-plugins>`.

    .. attribute:: assignmentgroups

        A set of the assignmentgroups for this assignment.

    .. attribute:: filenames
    
        A optional string of filenames separated by whitespace.
    """

    class Meta:
        verbose_name = _('Assignment')
        verbose_name_plural = _('Assignments')
        unique_together = ('short_name', 'parentnode')

    short_name = ShortNameField()
    long_name = LongNameField()
    parentnode = models.ForeignKey(Period, related_name='assignments')
    publishing_time = models.DateTimeField()
    anonymous = models.BooleanField(default=False)
    admins = models.ManyToManyField(User, blank=True)
    grade_plugin = models.CharField(max_length=100,
            choices=gradeplugin.registry,
            default=gradeplugin.registry.getdefaultkey())
    filenames = models.TextField(blank=True, null=True,
            help_text=_('Filenames separated by newline or space. If '
                'filenames are used, students will not be able to deliver '
                'files where the filename is not among the given filenames.'))

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
                    raise ValueError(_("Invalid filename: %(filename)s." %
                        dict(filename=filename)))

    @classmethod
    def where_is_admin(cls, user_obj):
        """ Returns a QuerySet matching all Assignments where the given user is admin.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return Assignment.objects.filter(
                Q(admins=user_obj) |
                Q(parentnode__admins=user_obj) |
                Q(parentnode__parentnode__admins=user_obj) |
                Q(parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))
        ).distinct()

    @classmethod
    def where_is_examiner(cls, user_obj):
        """ Get all assignments where the given ``user_obj`` is examiner on one
        of its assignment groups.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return Assignment.objects.filter(
            assignmentgroups__examiners=user_obj
            ).distinct()

    @classmethod
    def published_where_is_examiner(cls, user_obj):
        """ Get all :ref:`published <assignment-classifications>`
        assignments where the given ``user_obj`` is examiner on one of its
        assignment groups.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return Assignment.objects.filter(
            publishing_time__lt = datetime.now(),
            assignmentgroups__examiners=user_obj
            ).distinct()

    @classmethod
    def active_where_is_examiner(cls, user_obj):
        """ Get all :ref:`active <assignment-classifications>` assignments 
        where the given ``user_obj`` is examiner on one of its assignment
        groups.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        now = datetime.now()
        return Assignment.objects.filter(
            publishing_time__lt = now,
            parentnode__end_time__gt = now,
            assignmentgroups__examiners=user_obj
            ).distinct()

    @classmethod
    def old_where_is_examiner(cls, user_obj):
        """ Get all :ref:`old <assignment-classifications>` assignments
        where the given ``user_obj`` is examiner on one of its assignment
        groups.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        now = datetime.now()
        return Assignment.objects.filter(
            parentnode__end_time__lt = now,
            assignmentgroups__examiners=user_obj
            ).distinct()


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
    
    def assignment_groups_where_is_examiner_or_admin(self, user_obj):
        """ Get all assignment groups within this assignment where the given
        ``user_obj`` is examiner or is admin.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
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
        if self.publishing_time != None:
            if self.publishing_time < self.parentnode.start_time  or \
                    self.publishing_time > self.parentnode.end_time:
                raise ValidationError(
                    _("Publishing time must be within it's period (%(period)s)."
                      % dict(period=unicode(self.parentnode))))
       
        super(Assignment, self).clean(*args, **kwargs)


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
class AssignmentGroup(models.Model, CommonInterface):
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
    """

    parentnode = models.ForeignKey(Assignment, related_name='assignmentgroups')
    name = models.CharField(max_length=30, blank=True, null=True)
    examiners = models.ManyToManyField(User, blank=True,
            related_name="examiners")
    is_open = models.BooleanField(blank=True, default=True,
            help_text = _('If this is checked, the group can add deliveries.'))
    
    
    @classmethod
    def where_is_admin(cls, user_obj):
        """ Returns a QuerySet matching all AssignmentGroups where the
        given user is admin.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return AssignmentGroup.objects.filter(
                Q(parentnode__admins=user_obj) |
                Q(parentnode__parentnode__admins=user_obj) |
                Q(parentnode__parentnode__parentnode__admins=user_obj) |
                Q(parentnode__parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))
        ).distinct()

    @classmethod
    def where_is_candidate(cls, user_obj):
        """ Returns a QuerySet matching all AssignmentGroups where the
        given user is student.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return AssignmentGroup.objects.filter(candidates__student=user_obj)

    @classmethod
    def published_where_is_candidate(cls, user_obj):
        """ Returns a QuerySet matching all :ref:`published
        <assignment-classifications>` assignment groups where the given user
        is student.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return cls.where_is_candidate(user_obj).filter(
                parentnode__publishing_time__lt = datetime.now())

    @classmethod
    def active_where_is_candidate(cls, user_obj):
        """ Returns a QuerySet matching all :ref:`active
        <assignment-classifications>` assignment groups where the given user
        is student.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        now = datetime.now()
        return cls.published_where_is_candidate(user_obj).filter(
                parentnode__parentnode__start_time__lt = now,
                parentnode__parentnode__end_time__gt = now)

    @classmethod
    def old_where_is_candidate(cls, user_obj):
        """ Returns a QuerySet matching all :ref:`old
        <assignment-classifications>` assignment groups where the given user
        is student.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        now = datetime.now()
        return cls.where_is_candidate(user_obj).filter(
                parentnode__parentnode__end_time__lt = now)


    @classmethod
    def where_is_examiner(cls, user_obj):
        """ Returns a QuerySet matching all AssignmentGroups where the
        given user is examiner.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return AssignmentGroup.objects.filter(examiners=user_obj)

    @classmethod
    def published_where_is_examiner(cls, user_obj):
        """ Returns a QuerySet matching all :ref:`published
        <assignment-classifications>` assignment groups where the given user
        is examiner.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return cls.where_is_examiner(user_obj).filter(
                parentnode__publishing_time__lt = datetime.now())

    @classmethod
    def active_where_is_examiner(cls, user_obj):
        """ Returns a QuerySet matching all :ref:`active
        <assignment-classifications>` assignment groups where the given user
        is examiner.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        now = datetime.now()
        return cls.published_where_is_examiner(user_obj).filter(
                parentnode__parentnode__end_time__gt = now)
    
    @classmethod
    def old_where_is_examiner(cls, user_obj):
        """ Returns a QuerySet matching all :ref:`old
        <assignment-classifications>` assignment groups where the given user
        is examiner.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        now = datetime.now()
        return cls.where_is_examiner(user_obj).filter(
                parentnode__parentnode__end_time__lt = now)

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
    get_students.short_description = _('Students')
 
    def get_candidates(self):
        """ Get a string containing all candiates in the group separated by
        comma and a space, like: ``superman, spiderman, batman`` for normal
        assignments, and something like: ``321, 1533, 111`` for anonymous
        assignments.
        """
        return u', '.join(
                [c.get_identifier() for c in self.candidates.all()])
    get_students.short_description = _('Students')

    def get_examiners(self):
        """ Get a string contaning all examiners in the group separated by
        comma (``','``). """
        return u', '.join([u.username for u in self.examiners.all()])
    get_examiners.short_description = _('Examiners')

    def is_admin(self, user_obj):
        return self.parentnode.is_admin(user_obj)

    def is_candidate(self, user_obj):
        return self.candidates.filter(student=user_obj).count() > 0

    def is_examiner(self, user_obj):
        """ Return True if user is examiner on this assignment group """
        return self.examiners.filter(pk=user_obj.pk).count() > 0

    def get_status(self):
        """ Get status as a translated string.
        
        Returns one of:
            
            - "No deliveries"
            - "Not corrected"
            - "Corrected"
        """
        if self.deliveries.all().count() == 0:
            return _('No deliveries')
        else:
            qry = self.deliveries.filter(
                    feedback__published=True)
            if qry.count() == 0:
                return _('Not corrected')
            else:
                return _('Corrected')

    def get_latest_delivery(self):
        """ Get the latest delivery by this assignment group with feedback,
        or ``None`` if there is no deliveries with feedback. """
        if self.deliveries.all().count() == 0:
            return None
        else:
            qry = self.deliveries.filter(feedback__isnull=False)
            if qry.count() == 0:
                return None
            else:
                return qry.annotate(
                        models.Max('time_of_delivery'))[0]

    def get_grade_as_short_string(self):
        """ Get the grade  """
        q = self.get_deliveries_with_published_feedback().order_by('-time_of_delivery')
        if q.count() > 0:
            return q[0].feedback.get_grade_as_short_string()
        else:
            return None

    def get_number_of_deliveries(self):
        """ Get the number of deliveries by this assignment group. """
        return self.deliveries.all().count()

    def get_deliveries_with_published_feedback(self):
        """
        Get the the deliveries by this assignment group which have
        published feedback.
        """
        return self.deliveries.filter(feedback__published=True)

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
    
    def can_add_deliveries(self):
        """ Returns true if a student can add deliveries on this assignmengroup
        
        Both the assignmentgroups is_open attribute, and the periods start
        and end time is checked.
        """
        return self.is_open and self.parentnode.parentnode.is_active()


    def get_active_deadline(self):
        """ Get the active deadline. Checked id the following order:
            
            1. None if no deadline is set.
            2. First deadline after current date/time.
            3. Previous deadline before current date/time.
        """
        if self.deadlines.all().count() == 0:
            return None
        now = datetime.now()
        d = self.deadlines.filter(
                deadline__gt=now).order_by('deadline')
        if d.count() == 0:
            d = self.deadlines.filter(
                    deadline__lt=now).order_by('-deadline')
            return d[0]
        else:
            return d[0]


class Deadline(models.Model):
    """
    .. attribute:: assignment_group

        The assignment group where the deadline is registered.

    .. attribute:: deadline

        The deadline a DateTimeField.

    .. attribute:: text

        A optional deadline text.
    """
    assignment_group = models.ForeignKey(AssignmentGroup,
            related_name='deadlines') 
    deadline = models.DateTimeField()
    text = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('Deadline')
        verbose_name_plural = _('Deadlines')
        ordering = ['-deadline']
    
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
        """ Return True if :attr:`deadline` is in the past. """
        return self.deadline < datetime.now()


# TODO: Constraint: Can only be delivered by a person in the assignment group?
#                   Or maybe an administrator?
class Delivery(models.Model):
    """ A class representing a given delivery from an `AssignmentGroup`_.


    .. attribute:: assignment_group

        A django.db.models.ForeignKey_ pointing to the `AssignmentGroup`_
        that handed in the Delivery.

    .. attribute:: time_of_delivery

        A django.db.models.DateTimeField_ that holds the date and time the
        Delivery was uploaded.

    .. attribute:: number

        A django.db.models.PositiveIntegerField_ with the delivery-number
        within this assignment-group. This number is automatically
        incremented within each assignmentgroup, starting from 1. Must be
        unique within the assignment-group. Automatic incrementation is used
        if number is None when calling :meth:`save` (or :meth:`begin`).

    .. attribute:: delivered_by

        A django.db.models.ForeignKey_ pointing to the user that uploaded
        the Delivery

    .. attribute:: successful

        A django.db.models.BooleanField_ telling whether or not the Delivery
        was successfully uploaded.

    .. attribute:: filemetas

        A set of filemetas for this delivery.

    .. attribute:: feedback

       A django.db.models.OneToOneField to Feedback.

    """
    
    assignment_group = models.ForeignKey(AssignmentGroup, related_name='deliveries')
    time_of_delivery = models.DateTimeField()
    number = models.PositiveIntegerField()
    delivered_by = models.ForeignKey(User) # TODO: should be candidate!
    successful = models.BooleanField(blank=True, default=False)

    class Meta:
        verbose_name = _('Delivery')
        verbose_name_plural = _('Deliveries')
        ordering = ['-time_of_delivery']
        unique_together = ('assignment_group', 'number')

    @classmethod
    def where_is_admin(cls, user_obj):
        """ Returns a QuerySet matching all Deliveries where the given user
        is admin.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return Delivery.objects.filter(
                Q(assignment_group__parentnode__admins=user_obj) |
                Q(assignment_group__parentnode__parentnode__admins=user_obj) |
                Q(assignment_group__parentnode__parentnode__parentnode__admins=user_obj) |
                Q(assignment_group__parentnode__parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))
        ).distinct()

    @classmethod
    def begin(cls, assignment_group, user_obj):
        """ Begin delivery.

        Creates a delivery with ``time_of_delivery`` set to current time,
        ``delivered_by`` set to the given ``user_obj``, ``assignment_group``
        set to the given ``assignment_group`` and successful set to
        ``false``.

        This should be followed up by one or more calls to :meth:`add_file`
        on the returned FileMeta-object, and completed by calling
        :meth:`finish`.
        """
        d = Delivery()
        d.assignment_group = assignment_group
        d.time_of_delivery = datetime.now()
        d.delivered_by = user_obj
        d.successful = False
        d.save()
        return d

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

    def finish(self):
        """ Finish the delivery by updating the time of delivery, marking it
        as successful and saving. """
        self.time_of_delivery = datetime.now()
        self.successful = True
        self.save()

    def get_feedback(self):
        """ Get the feedback for this delivery. If the feedback does not
        exists, a new :class:`Feedback`-object is created but not saved.

        :return:
            A :class:`Feedback`-object with the delivery-attribute set
            to this delivery.
        """
        try:
            return self.feedback
        except Feedback.DoesNotExist:
            return Feedback(delivery=self)

    def get_status(self):
        """ Get the status for this delivery; 'Corrected' or
        'Not Corrected'.
        """
        try:
            if self.feedback.published:
                return _("Corrected")
        except Feedback.DoesNotExist:
            pass
        return _("Not Corrected")
            
    def save(self, *args, **kwargs):
        """
        Set :attr:`number` automatically to one greater than what is was
        last.
        """
        if not self.number:
            m = Delivery.objects.filter(
                    assignment_group=self.assignment_group).aggregate(
                            Max('number'))
            self.number = (m['number__max'] or 0) + 1
        super(Delivery, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s %s' % (self.assignment_group, self.time_of_delivery)



# TODO: Refactor feedback_* to just *.
class Feedback(models.Model):
    """
    Represents the feedback for a given `Delivery`_.

    .. attribute:: text

       A django.db.models.TextField_ that holds the feedback text given by
       the examiner.

    .. attribute:: format

       A django.db.models.CharField_ that holds the format of the feedback
       text. Valid values are:

           ``"rst"``
               Format feedback using restructured text.

           ``"text"``
               Plain text - no text formatting.

    .. attribute:: published

       A django.db.models.BooleanField_ that tells if the feedback is
       published or not. This allows editing and saving the feedback before
       publishing it. Is useful for exams and other assignments when
       feedback and grading is published simultaneously for all Deliveries.

    .. attribute:: delivery

       A django.db.models.OneToOneField_ that points to the `Delivery`_ to
       be given feedback.

    .. attribute:: grade
    
       A generic relation
       (django.contrib.contenttypes.generic.GenericForeignKey) to the
       grade-plugin object storing the grade for this feedback. This will
       always be a subclass of
       :class:`devilry.core.gradeplugin.GradeModel`. The
       :meth:`clean`-method checks that this points to a class of the type
       defined in :attr:`Assignment.grade_plugin`.
    """

    text_formats = (
       ('rst', 'ReStructured Text'),
       ('txt', 'Text'),
    )
    text = models.TextField(blank=True, null=True, default='')
    format = models.CharField(max_length=20, choices=text_formats,
            default=text_formats[0])
    published = models.BooleanField(blank=True, default=False)
    delivery = models.OneToOneField(Delivery)
    last_modified = models.DateTimeField(auto_now=True, blank=False,
            null=False)
    last_modified_by = models.ForeignKey(User, blank=False, null=False)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    grade = generic.GenericForeignKey('content_type', 'object_id')

    def get_grade_as_short_string(self):
        """
        Get the grade as a short string suitable for short one-line
        display.
        """
        return self.grade.get_grade_as_short_string(self)

    def get_grade_as_long_string(self):
        """
        Get the grade as a longer string formatted with restructured
        text.

        :return:
            None if getting long string is not supported by the grade
            plugin.
        """
        return self.grade.get_grade_as_long_string(self)

    def set_grade_from_xmlrpcstring(self, grade):
        """
        Set the grade from string. This is primarly intended for xmlrpc, and
        a grade-plugin is not required to support it.
        
        Raises :exc:`NotImplementedError` if the grade-plugin do not support
        setting grades from string.

        Raises :exc:`ValueError` if the grade-plugin given grade is invalid
        for this grade-plugin. The error message in the exception is suited
        for direct display to the user.
        """
        key = self.delivery.assignment_group.parentnode.grade_plugin
        model_cls = gradeplugin.registry.getitem(key).model_cls
        if self.grade:
            ok_message = self.grade.set_grade_from_xmlrpcstring(grade, self)
            self.grade.save()
        else:
            gradeobj = model_cls()
            ok_message = gradeobj.set_grade_from_xmlrpcstring(grade, self)
            gradeobj.save()
            self.grade = gradeobj
        return ok_message

    def get_grade_as_xmlrpcstring(self):
        """
        Get the grade as a string compatible with
        :meth:`set_grade_from_xmlrpcstring`. This is primarly intended for xmlrpc,
        and a grade-plugin is not required to support it.

        If you need a simple string representation, use :meth:`get_grade_as_short_string`
        instead.

        Raises :exc:`NotImplementedError` if the grade-plugin do not support
        getting grades as string.

        :return:
            None if getting grade as xmlrpcstring is not supported by
            the grade plugin.
        """
        return self.grade.get_grade_as_xmlrpcstring(self)
        
    def get_assignment(self):
        """
        Shortcut for getting the assignment
        (``delivery.assignment_group.parentnode``).
        """
        return self.delivery.assignment_group.parentnode

    def clean(self, *args, **kwargs):
        """Validate the Feedback, making sure it does not do something stupid.

        Always call this before save()! Read about validation here:
        http://docs.djangoproject.com/en/dev/ref/models/instances/#id1

        Raises ValidationError if:

            - :attr:`grade` is not a instance of the model-class
              defined in
              :attr:`devilry.core.gradeplugin.RegistryItem.model_cls`
              referred by :attr:`Assignment.grade_plugin`.
            - The node is the child of itself or one of its childnodes.
        """

        #    raise ValidationError(_('A node can not be it\'s own parent.'))
        assignment = self.delivery.assignment_group.parentnode
        try:
            ri = self.get_assignment().get_gradeplugin_registryitem()
        except KeyError, e:
            raise ValidationError(_(
                'The assignment, %s, has a invalid grade-plugin. Contact ' \
                'the system administrators to get this fixed.' %
                assignment))
        else:
            if self.grade:
                if not isinstance(self.grade, ri.model_cls):
                    raise ValidationError(_(
                        'Grade-plugin on feedback must be "%s", as on the ' \
                        'assignment, %s.' % (ri.label, assignment)))

        super(Feedback, self).clean(*args, **kwargs)


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

        The current :ref:`DeliveryStore <ref-devilry.core.deliverystore>`.
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

from django.db.models.signals import pre_delete
pre_delete.connect(filemeta_deleted_handler, sender=FileMeta)
pre_delete.connect(feedback_grade_delete_handler, sender=Feedback)
