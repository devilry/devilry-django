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
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.formats import date_format

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

    def clean(self, *args, **kwargs):
        super(Subject, self).clean(*args, **kwargs)


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
    minimum_points = models.PositiveIntegerField(default=0,
            help_text=_('Students must get at least this many points to '\
                    'pass the period.'))

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

        A set of the assignmentgroups for this assignment.

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

        The maximum number of points possible without scaling. This is set
        using :meth:`devilry.core.gradeplugin.GradeModel.get_maxpoints`.

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
    """

    class Meta:
        verbose_name = _('Assignment')
        verbose_name_plural = _('Assignments')
        unique_together = ('short_name', 'parentnode')

    short_name = ShortNameField()
    long_name = LongNameField()
    parentnode = models.ForeignKey(Period, related_name='assignments')
    publishing_time = models.DateTimeField(
            verbose_name=_("Publishing time"))
    anonymous = models.BooleanField(default=False,
            verbose_name=_("Anonymous"))
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


    def _get_maxpoints(self):
        gradeplugincls = self.get_gradeplugin_registryitem().model_cls
        if self.id == None:
            return gradeplugincls.get_maxpoints()
        else:
            return gradeplugincls.get_maxpoints(self)

    def _update_scalepoints(self):
        for group in self.assignmentgroups.iterator():
            group.scaled_points = group._get_scaled_points()
            group.save()

    def save(self, *args, **kwargs):
        """ Save and recalculate the value of :attr:`maxpoints` and
        :attr:`pointscale`. """
        self.maxpoints = self._get_maxpoints()
        if self.autoscale:
            self.pointscale = self.maxpoints
        super(Assignment, self).save()
        self._update_scalepoints()

    def get_gradeplugin_registryitem(self):
        """ Get the :class:`devilry.core.gradeplugin.RegistryItem`
        for the current :attr:`grade_plugin`. """
        return gradeplugin.registry.getitem(self.grade_plugin)

    def validate_gradeplugin(self):
        """ Check if grade plugin is valid (exists). 
        Raise :exc:`devilry.core.gradeplugin.GradePluginDoesNotExistError`
        on error. """
        try:
            ri = self.get_gradeplugin_registryitem()
        except KeyError, e:
            raise gradeplugin.GradePluginDoesNotExistError(
                'Invalid grade plugin "%s" on assignment: %s. This is '\
                'usually because a grade plugin has been removed from '\
                'the INSTALLED_APPS setting. There is no easy fix for '\
                'this except to re-enable the missing grade plugin.' % (
                    self.grade_plugin, self))

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

    .. attribute:: status

        Stores data that can be deduces from other data in the database, but
        since this requires complex queries, we store it as a integer
        instead, with the following values:

            0. No deliveries
            1. Not corrected
            2. Corrected, not published
            3. Corrected and published
                The group has at least one published feedback.

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

    .. attribute:: NO_DELIVERIES

        The numberic value corresponding to :attr:`status` *no deliveries*.

    .. attribute:: NOT_CORRECTED

        The numberic value corresponding to :attr:`status` *not corrected*.

    .. attribute:: CORRECTED_NOT_PUBLISHED

        The numberic value corresponding to :attr:`status` *corrected, not
        published*.

    .. attribute:: CORRECTED_AND_PUBLISHED

        The numberic value corresponding to :attr:`status` *corrected, and
        published*.
    """
    status_mapping = (
        _("No deliveries"),
        _("Not corrected"),
        _("Corrected, not published"),
        _("Corrected and published"),
    )
    status_mapping_student = (
        status_mapping[0],
        status_mapping[1],
        status_mapping[1], # "not published" means not "not corrected" is displayed to the student
        _("Corrected"),
    )
    status_mapping_cssclass = (
        _("status_no_deliveries"),
        _("status_not_corrected"),
        _("status_corrected_not_published"),
        _("status_corrected_and_published"),
    )
    status_mapping_student_cssclass = (
        status_mapping_cssclass[0],
        status_mapping_cssclass[1],
        status_mapping_cssclass[1], # "not published" means "not corrected" is displayed to the student
        status_mapping_cssclass[3],
    )
    NO_DELIVERIES = 0
    NOT_CORRECTED = 1
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
    points = models.PositiveIntegerField(default=0,
            help_text=_('Final number of points for this group. This '\
                'number is controlled by the grade plugin, and should not '\
                'be changed manually.'))
    scaled_points = models.FloatField(default=0.0)
    is_passing_grade = models.BooleanField(default=False)


    def _get_scaled_points(self):
        scale = float(self.parentnode.pointscale)
        maxpoints = self.parentnode.maxpoints
        if maxpoints == 0:
            return 0.0
        return (scale/maxpoints) * self.points

    def save(self, *args, **kwargs):
        self.scaled_points = self._get_scaled_points()
        super(AssignmentGroup, self).save(*args, **kwargs)
    
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

    def can_examine(self, user_obj):
        """ Return True if the user has permission to examine (creeate
        feedback and browse files) on this assignment group.
        
        Examiners, admins and superusers has this permission. """
        return user_obj.is_superuser or self.is_admin(user_obj) \
                or self.is_examiner(user_obj)

    def get_localized_status(self):
        """ Returns the current status string from :attr:`status_mapping`. """
        return self.status_mapping[self.status]

    def get_localized_student_status(self):
        """ Returns the current status string from
        :attr:`status_mapping_student`. """
        return self.status_mapping_student[self.status]

    def get_status_cssclass(self):
        """ Returns the current status string from
        :attr:`status_mapping_cssclass`. """
        return self.status_mapping_cssclass[self.status]

    def get_status_student_cssclass(self):
        """ Returns the current status string from
        :attr:`status_mapping_student_cssclass`. """
        return self.status_mapping_student_cssclass[self.status]

    def _get_status_from_qry(self):
        if self.deliveries.all().count() == 0:
            return self.NO_DELIVERIES
        else:
            qry = self.deliveries.filter(
                    feedback__isnull=False)
            if qry.count() == 0:
                return self.NOT_CORRECTED
            else:
                qry = qry.filter(feedback__published=True)
                if qry.count() == 0:
                    return self.CORRECTED_NOT_PUBLISHED
                else:
                    return self.CORRECTED_AND_PUBLISHED

    def _update_status(self):
        """ Query for the correct status, and set :attr:`status`. """
        self.status = self._get_status_from_qry()

    def get_number_of_deliveries(self):
        """ Get the number of deliveries by this assignment group. """
        return self.deliveries.all().count()

    def get_latest_delivery(self):
        """ Get the latest delivery by this assignment group,
        or ``None`` if there is no deliveries. """
        qry = self.deliveries.all()
        if qry.count() == 0:
            return None
        else:
            return qry.annotate(
                    models.Max('time_of_delivery'))[0]

    def get_latest_delivery_with_feedback(self):
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

    def get_deliveries_with_published_feedback(self):
        """
        Get the the deliveries by this assignment group which have
        published feedback.
        """
        return self.deliveries.filter(feedback__published=True)

    def get_latest_delivery_with_published_feedback(self):
        """
        Get the latest delivery with published feedback.
        """
        q = self.get_deliveries_with_published_feedback().order_by(
                '-time_of_delivery')
        if q.count() == 0:
            return None
        else:
            return q[0]

    def _get_gradeplugin_cached_fields(self):
        d = self.get_latest_delivery_with_published_feedback()
        points = 0
        if self.parentnode.must_pass:
            is_passing_grade = False
            if d:
                is_passing_grade = d.feedback.get_grade().is_passing_grade()
        else:
            is_passing_grade = True
        if d:
            points = d.feedback.grade.get_points()
        return points, is_passing_grade

    def update_gradeplugin_cached_fields(self):
        self.points, self.is_passing_grade = self._get_gradeplugin_cached_fields()
        self.save()

    def get_grade_as_short_string(self):
        """ Get the grade as a "short string". """
        d = self.get_latest_delivery_with_published_feedback()
        if not d:
            return None
        else:
            return d.feedback.get_grade_as_short_string()

    def can_save(self, user_obj):
        """ Check if the user has permission to save this AssignmentGroup.
        This only runs :meth:`Assignment.is_admin`, so there is no need to
        use this if you have already used can_save() on the
        :attr:`parentnode`. """
        if user_obj.is_superuser:
            return True
        elif self.parentnode:
            return self.parentnode.is_admin(user_obj)
        else:
            return False
    
    def can_add_deliveries(self):
        """ Returns true if a student can add deliveries on this assignmengroup
        
        Both the assignmentgroups is_open attribute, and the periods start
        and end time is checked.
        """
        return self.is_open and self.parentnode.parentnode.is_active()


    def get_active_deadline(self):
        """ Get the active deadline.
            
        :return:
            Latest deadline, or None if no deadline is set.
        """
        now = datetime.now()
        deadlines = self.deadlines.filter(deadline__gt=now).order_by('deadline')
        if len(deadlines) == 0:
            return None
        else:
            return deadlines[0]


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
        """ Return True if :attr:`deadline` expired. """
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

    .. attribute:: deadline_tag

       Adjango.db.models.ForeignKey_ pointing to the Deadline for this Delivery.

    .. attribute:: after_deadline

       A django.db.models.BooleanField_ denoting if the delivery was after the last deadline

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
    deadline_tag = models.ForeignKey(Deadline, blank=True, null=True, on_delete=models.SET_NULL, related_name='deliveries')
    after_deadline = models.BooleanField(default=False)
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
        
        # Find correct deadline and tag the delivery 
        last_deadline = None
        for tmp in assignment_group.deadlines.all().order_by('deadline'):
            last_deadline = tmp
            if d.time_of_delivery < tmp.deadline:
                d.deadline_tag = tmp
                break
        # Delivered too late, so tag with 'after_deadline'
        if d.deadline_tag == None and not last_deadline == None:
            d.deadline_tag = last_deadline
            d.after_deadline = True
        
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

    def get_status_number(self):
        """ Get the numeric status for this delivery.

        :return: The numeric status:
            :attr:`AssignmentGroup.NOT_CORRECTED`,
            :attr:`AssignmentGroup.CORRECTED_NOT_PUBLISHED` or
            :attr:`AssignmentGroup.CORRECTED_AND_PUBLISHED`.
        """
        try:
            if self.feedback.published:
                return AssignmentGroup.CORRECTED_AND_PUBLISHED
            else:
                return AssignmentGroup.CORRECTED_NOT_PUBLISHED
        except Feedback.DoesNotExist:
            pass
        return AssignmentGroup.NOT_CORRECTED

    def get_localized_status(self):
        """
        Returns the current status string from
        :attr:`AssignmentGroup.status_mapping`.
        """
        status = self.get_status_number()
        return AssignmentGroup.status_mapping[status]

    def get_localized_student_status(self):
        """
        Returns the current status string from
        :attr:`AssignmentGroup.status_mapping_student`.
        """
        status = self.get_status_number()
        return AssignmentGroup.status_mapping_student[status]

    def get_status_cssclass(self):
        """ Returns the css class for the current status from
        :attr:`AssignmentGroup.status_mapping_cssclass`. """
        return AssignmentGroup.status_mapping_cssclass[self.get_status_number()]

    def get_status_student_cssclass(self):
        """ Returns the css class for the current status from
        :attr:`AssignmentGroup.status_mapping_student_cssclass`. """
        return AssignmentGroup.status_mapping_student_cssclass[
                self.get_status_number()]
            
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
        return u'%s - %s (%s)' % (self.assignment_group, self.number,
                date_format(self.time_of_delivery, "DATETIME_FORMAT"))



class Feedback(models.Model):
    """
    Represents the feedback for a given `Delivery`_.

    Typical usage for manual manipulation of feedbacks (in tests and xmlrpc)::

        test = Assignment(
                parentnode = Period.objects.get(pk=1),
                publishing_time = datetime.now(),
                anonymous = False,
                grade_plugin = "grade_approved:approvedgrade")
        group = test.assignmentgroups.create(name="My group")
        delivery = Delivery.begin(group, User.objects.get(username="student1"))
        delivery.add_file("test.txt", ["test"])
        delivery.finish()
        feedback = delivery.get_feedback()
        feedback.last_modified_by = User.objects.get(username="examiner1")
        feedback.set_grade_from_xmlrpcstring("approved")
        feedback.save()

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

    .. attribute:: last_modified_by

       The django.contrib.auth.models.User_ that last modified the feedback.

    .. attribute:: last_modified

       Date/time of last modification.

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
       ('txt', 'Plain text'),
    )
    text = models.TextField(blank=True, null=True, default='',
            verbose_name = _('Feedback text'))
    format = models.CharField(max_length=20, choices=text_formats,
            default = text_formats[0],
            verbose_name = _('Feedback text format'),
            help_text = _(
                'Unless you have problems with "ReStructured Text", you '\
                'should use it, as it allows you to mark up your ' \
                'feedback and thus make it more readable by the student. ' \
                'Only use "Plain text" as a fallback/last resort.')
            )
    published = models.BooleanField(blank=True, default=False,
            verbose_name = _('Published'),
            help_text = _(
                'Check this to make the feedback visible to the student(s).'))
    delivery = models.OneToOneField(Delivery)
    last_modified = models.DateTimeField(auto_now=True, blank=False,
            null=False)
    last_modified_by = models.ForeignKey(User, blank=False, null=False)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    grade = generic.GenericForeignKey('content_type', 'object_id')


    def save(self, *args, **kwargs):
        super(Feedback, self).save(*args, **kwargs)
        self.delivery.assignment_group.update_gradeplugin_cached_fields()

    def __unicode__(self):
        return "Feedback on %s" % self.delivery

    def get_grade_object_info(self):
        """ Get information about the grade object as a string. """
        return 'content_type: %s, object_id:%s, ' \
                'grade: %s' % (self.content_type, self.object_id,
                        self.grade)

    def get_grade(self):
        """ Get :attr:`grade`, but raise :exc:`ValueError` if the grade
        object is not a subclass of
        :class:`devilry.core.gradeplugin.GradeModel`. """
        if self.grade:
            self.validate_gradeobj()
        return self.grade

    def validate_gradeobj(self):
        """ Validate the grade object integrity. When this fails, the
        database integrity is corrupt. Raises one of the subclasses of
        :exc:`devilry.core.gradeplugin.GradePluginError` on error. """
        assignment = self.delivery.assignment_group.parentnode
        try:
            ri = self.get_assignment().get_gradeplugin_registryitem()
        except KeyError, e:
            raise gradeplugin.GradePluginDoesNotExistError('Feedback with '\
                    'id %s (%s) belongs in a assignment (%s) with a '\
                    'invalid gradeplugin. ' % (
                        self.id, self, assignment))
        if not isinstance(self.grade, ri.model_cls):
            correct_ct = ri.get_content_type()
            raise gradeplugin.WrongContentTypeError(
                'Grade-plugin on feedback with id "%s" (%s) must be "%s", as on the ' \
                'assignment: %s. It is: %s. The content type on the feedback '\
                'should be "%s (pk:%s)", not "%s (pk:%s)".' % (self.id, self, ri.get_key(), assignment,
                    self.get_grade_object_info(),
                    correct_ct, correct_ct.pk, 
                    self.content_type, self.content_type.pk))

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
            self.grade.save(self)
        else:
            gradeobj = model_cls()
            ok_message = gradeobj.set_grade_from_xmlrpcstring(grade, self)
            gradeobj.save(self)
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
        if self.grade:
            self.validate_gradeobj()
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


def feedback_update_assignmentgroup_status_handler(sender, **kwargs):
    feedback = kwargs['instance']
    feedback.delivery.assignment_group._update_status()
    feedback.delivery.assignment_group.save()

def delivery_update_assignmentgroup_status_handler(sender, **kwargs):
    delivery = kwargs['instance']
    delivery.assignment_group._update_status()
    delivery.assignment_group.save()

from django.db.models.signals import pre_delete, post_save
pre_delete.connect(filemeta_deleted_handler, sender=FileMeta)
pre_delete.connect(feedback_grade_delete_handler, sender=Feedback)
post_save.connect(feedback_update_assignmentgroup_status_handler,
        sender=Feedback)
post_save.connect(delivery_update_assignmentgroup_status_handler,
        sender=Delivery)
