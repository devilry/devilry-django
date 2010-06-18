from datetime import datetime

from django.db.models.signals import post_save, post_delete
from django.db import models
from django.contrib.auth.models import User, Permission
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from deliverystore import load_deliverystore_backend
import gradeplugin_registry



# TODO: Subject.short_name unique for efficiency and because it is common at universities. Other schools can prefix to make it unique in any case.
# TODO: Paths should be something like get_full_path() and get_unique_path(), where the latter considers Subject.short_name as unique
# TODO: indexes
# TODO: Complete/extend and document CommonInterface.
# TODO: Clean up the __unicode__ mess with paths.
# TODO: Check that the *_where_* methods in AssignmentGroup are needed/appropriate


class CommonInterface(object):

    @classmethod
    def where_is_admin(cls, user_obj):
        """ Get all objects of this type where the given user is admin. """
        raise NotImplementedError()
    



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
            help_text=_("Max 20 characters. Only numbers, letters, '_' and '-'."))
        kw.update(kwargs)
        super(ShortNameField, self).__init__(*args, **kw)


class LongNameField(models.CharField):
    def __init__(self, *args, **kwargs):
        kw = dict(max_length=100,
            verbose_name='Long name',
            db_index = True,
            help_text=_('A longer name, more descriptive than "Short name".'))
        kw.update(kwargs)
        super(LongNameField, self).__init__(*args, **kw)


class BaseNode(CommonInterface):
    """
    The base class of the Devilry hierarchy. Implements basic functionality
    used by the other Node classes. This is a abstract datamodel, so it
    is never used directly.

    .. attribute:: short_name

        A django.db.models.SlugField_ with max 20 characters. Only numbers,
        letters, '_' and '-'.

    .. attribute:: long_name

        A django.db.models.CharField_ with max 100 characters. Gives a longer 
        description than :attr:`short_name`

    .. _django.db.models.SlugField: http://docs.djangoproject.com/en/dev/ref/models/fields/#slugfield
    .. _django.db.models.CharField: http://docs.djangoproject.com/en/dev/ref/models/fields/#charfield
    .. _django.db.models.ForeignKey: http://docs.djangoproject.com/en/dev/ref/models/fields/#foreignkey
    .. _django.db.models.ManyToManyField: http://docs.djangoproject.com/en/dev/ref/models/fields/#manytomanyfield
    .. _django.db.models.DateTimeField: http://docs.djangoproject.com/en/dev/ref/models/fields/#datetimefield
    .. _django.db.models.BooleanField: http://docs.djangoproject.com/en/dev/ref/models/fields/#booleanfield
    .. _django.db.models.OneToOneField: http://docs.djangoproject.com/en/dev/ref/models/fields/#onetoonefield
    .. _django.db.models.TextField: http://docs.djangoproject.com/en/dev/ref/models/fields/#textfield
    .. _django.contrib.auth.models.User: http://docs.djangoproject.com/en/dev/topics/auth/#users
    """

    def get_path(self):
        return unicode(self)
    get_path.short_description = _('Path')

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
        """ Check if the give user has permission to save (or create) this node.

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
    """
    short_name = ShortNameField()
    long_name = LongNameField()
    parentnode = models.ForeignKey('self', blank=True, null=True)
    admins = models.ManyToManyField(User, blank=True)

    class Meta:
        verbose_name = _('Node')
        verbose_name_plural = _('Nodes')
        unique_together = ('short_name', 'parentnode')


    def _can_save_id_none(self, user_obj):
        return False

    def __unicode__(self):
        return self.get_path()

    def get_path(self):
        if self.parentnode:
            return self.parentnode.get_path() + "." + self.short_name
        else:
            return self.short_name


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
                add_admnodes(a.node_set)
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
    def _get_pathlist_kw(cls, pathlist):
        """ Used by get_by_pathlist to create the required kwargs for
        Node.objects.get(). Might be a starting point for more sophisticated
        queries including paths. """
        kw = {}
        key = 'short_name'
        for short_name in reversed(pathlist):
            kw[key] = short_name
            key = 'parentnode__' + key
        return kw

    @classmethod
    def get_by_pathlist(cls, pathlist):
        """ Get node by pathlist.
        
        :param pathlist: A list of node-names, like ``['uio', 'ifi']``.
        :return: A Node-object.
        """
        return Node.objects.get(**cls._get_pathlist_kw(pathlist))

    @classmethod
    def get_by_path(cls, path):
        """ Get a node by path.
        
        :param path: Node-names separated by '.', like ``'uio.ifi'``.
        :type path: str
        :return: A Node-object.
        """
        return cls.get_by_pathlist(path.split('.'))


    @classmethod
    def create_by_pathlist(cls, pathlist):
        """ Create a new node from the path given in `nodelist`, creating all
        missing parents. """
        parent = None
        n = None
        for i, short_name in enumerate(pathlist):
            try:
                n = Node.get_by_pathlist(pathlist[:i+1])
            except Node.DoesNotExist, e:
                n = Node(short_name=short_name, long_name=short_name, parentnode=parent)
                n.save()
            parent = n
        return n

    @classmethod
    def create_by_path(cls, path):
        """ Just like `get_by_pathlist`, but the path is a string where each
        `short_name` is separated by '.', instead of a list. """
        return cls.create_by_pathlist(path.split('.'))


class Subject(models.Model, BaseNode):
    """
    This class represents a subject. This may be either a full course,
    or one part of a course, if it is divided into parallell courses.
    
    .. attribute:: parentnode
        
        A django.db.models.ForeignKey_ that points to the parent node,
        which is always a `Node`_.

    .. attribute:: admins
        
        A django.db.models.ManyToManyField_ that holds all the admins of the
        `Node`_.
    """

    class Meta:
        verbose_name = _('Subject')
        verbose_name_plural = _('Subjects')
        unique_together = ('short_name', 'parentnode')

    short_name = ShortNameField(unique=True)
    long_name = LongNameField()
    parentnode = models.ForeignKey(Node)
    admins = models.ManyToManyField(User, blank=True)
    
    @classmethod
    def where_is_admin(cls, user_obj):
        """ Returns a QuerySet matching all Subjects where the given user is admin.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return Subject.objects.filter(
                Q(admins__pk=user_obj.pk)
                | Q(parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))).distinct()

    def __unicode__(self):
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
    """

    class Meta:
        verbose_name = _('Period')
        verbose_name_plural = _('Periods')
        unique_together = ('short_name', 'parentnode')

    short_name = ShortNameField()
    long_name = LongNameField()
    parentnode = models.ForeignKey(Subject)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    admins = models.ManyToManyField(User, blank=True)


    @classmethod
    def where_is_admin(cls, user_obj):
        """ Returns a QuerySet matching all Periods where the given user is admin.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return Period.objects.filter(
                Q(admins=user_obj) |
                Q(parentnode__admins=user_obj) |
                Q(parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))
        ).distinct()

    def __unicode__(self):
        return u"%s / %s" % (self.parentnode, self.short_name)


# TODO: Constraint publishing_time by start_time and end_time
class Assignment(models.Model, BaseNode):
    """
    Represents one assignment for a given period in a given subject. May consist
    of several parts, which means that several exercises can be given as one 
    Assignment.

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

        A django.db.models.CharField_ that holds the current feedback plugin
        used.
    """

    class Meta:
        verbose_name = _('Assignment')
        verbose_name_plural = _('Assignments')
        unique_together = ('short_name', 'parentnode')

    short_name = ShortNameField()
    long_name = LongNameField()
    parentnode = models.ForeignKey(Period)
    publishing_time = models.DateTimeField()
    anonymous = models.BooleanField(default=False)
    deadline = models.DateTimeField()
    admins = models.ManyToManyField(User, blank=True)
    grade_plugin = models.CharField(max_length=100,
            choices=gradeplugin_registry.KeyLabelIterable())

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

    def __unicode__(self):
        return u"%s / %s" % (self.parentnode, self.short_name)

    @classmethod
    def where_is_examiner(cls, user_obj):
        """ Get all assignments where the given ``user_obj`` is examiner on one
        of its assignment groups.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return Assignment.objects.filter(
            assignmentgroup__examiners=user_obj
            ).distinct()

    def assignment_groups_where_is_examiner(self, user_obj):
        """ Get all assignment groups within this assignment where the given
        ``user_obj`` is examiner.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return self.assignmentgroup_set.filter(examiners=user_obj)
 



class Candidate(models.Model):
    student = models.ForeignKey(User)
    assignment_group = models.ForeignKey('AssignmentGroup')

    # TODO unique within assignment
    candidate_id = models.CharField(max_length=30, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.student)


# TODO: Constraint: cannot be examiner and student on the same assignment?
class AssignmentGroup(models.Model):
    """
    Represents a student or a group of students. 

    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node,
        which is always an `Assignment`_.

    .. attribute:: students

        A django.db.models.ManyToManyField_ that holds the student(s) that have
        handed in the assignment

    .. attribute:: examiners
        
        A django.db.models.ManyToManyField_ that holds the examiner(s) that are
        to correct and grade the assignment.

    .. attribute:: is_open

        A django.db.models.BooleanField_ that tells you if the group can add
        deliveries or not.
    """
    parentnode = models.ForeignKey(Assignment)

    students = models.ManyToManyField(User, blank=True, through=Candidate,
            related_name='candidates')

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
    def where_is_student(cls, user_obj):
        """ Returns a QuerySet matching all AssignmentGroups where the
        given user is student.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return AssignmentGroup.objects.filter(students=user_obj)

    @classmethod
    def published_where_is_student(cls, user_obj):
        """ Returns a QuerySet matching all published AssignmentGroups where
        the given user is student.

        A published AssignmentGroup is a assignment group where
        ``Assignment.publishing_time`` is in the past.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return cls.where_is_student(user_obj).filter(
                parentnode__publishing_time__lt = datetime.now())

    @classmethod
    def active_where_is_student(cls, user_obj):
        """ Returns a QuerySet matching all active AssignmentGroups where
        the given user is student.

        A active AssignmentGroup is a assignment group where
        ``Assignment.publishing_time`` is in the past and current time is
        between ``Period.start_time`` and ``Period.end_time``.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        now = datetime.now()
        return cls.published_where_is_student(user_obj).filter(
                parentnode__parentnode__start_time__lt = now,
                parentnode__parentnode__end_time__gt = now)

    @classmethod
    def old_where_is_student(cls, user_obj):
        """ Returns a QuerySet matching all active AssignmentGroups where
        the given user is student.

        A active AssignmentGroup is a assignment group where
        ``Period.end_time`` is in the past.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        now = datetime.now()
        return cls.where_is_student(user_obj).filter(
                parentnode__parentnode__end_time__lt = now)


    @classmethod
    def where_is_examiner(cls, user_obj):
        return AssignmentGroup.objects.filter(examiners=user_obj)

    @classmethod
    def published_where_is_examiner(cls, user_obj):
        return cls.where_is_examiner(user_obj).filter(
                parentnode__publishing_time__lt = datetime.now())

    @classmethod
    def active_where_is_examiner(cls, user_obj):
        now = datetime.now()
        return cls.published_where_is_examiner(user_obj).filter(
                parentnode__parentnode__start_time__lt = now,
                parentnode__parentnode__end_time__gt = now)
    
    @classmethod
    def old_where_is_examiner(cls, user_obj):
        now = datetime.now()
        return cls.where_is_examiner(user_obj).filter(
                parentnode__parentnode__end_time__lt = now)


    def __unicode__(self):
        return u'%s (%s)' % (self.parentnode.long_name,
                ', '.join([unicode(x) for x in self.students.all()]))
    
    def get_students(self):
        """ Get a string contaning all students in the group separated by
        comma (``','``). """
        return u', '.join([u.username for u in self.students.all()])
    get_students.short_description = _('Students')

    def get_examiners(self):
        """ Get a string contaning all examiners in the group separated by
        comma (``','``). """
        return u', '.join([u.username for u in self.examiners.all()])
    get_examiners.short_description = _('Examiners')

    def is_admin(self, user_obj):
        return self.parentnode.is_admin(user_obj)

    def is_student(self, user_obj):
        return self.students.filter(pk=user_obj.pk).count() > 0

    def is_examiner(self, user_obj):
        """ Return True if user is examiner on this assignment group """
        return self.examiners.filter(pk=user_obj.pk).count() > 0

    def get_status(self):
        if self.delivery_set.all().count() == 0:
            return _('No deliveries')
        else:
            qry = self.delivery_set.filter(feedback__isnull=False)
            if qry.count() == 0:
                return _('Not corrected')
            else:
                return _('Corrected')

    def get_grade(self):
        if self.delivery_set.all().count() == 0:
            return None
        else:
            qry = self.delivery_set.filter(feedback__isnull=False)
            if qry.count() == 0:
                return None
            else:
                return qry.annotate(
                        models.Max('time_of_delivery'))[0].feedback.get_grade()


    def get_number_of_deliveries(self):
        return self.delivery_set.all().count()


class Delivery(models.Model):
    """
    A class representing a given delivery from an `AssignmentGroup`_. In
    some cases, a group are allowed to hand in several deliveries per
    assignment.

    .. attribute:: assignment_group

        A django.db.models.ForeignKey_ pointing to the `AssignmentGroup`_
        that handed in the Delivery.

    .. attribute:: time_of_delivery

        A django.db.models.DateTimeField_ that holds the date and time the
        Delivery was uploaded.

    .. attribute:: delivered_by

        A django.db.models.ForeignKey_ pointing to the user that uploaded
        the Delivery

    .. attribute:: successful

        A django.db.models.BooleanField_ telling whether or not the Delivery was
        successfully uploaded.
    """
    
    assignment_group = models.ForeignKey(AssignmentGroup)
    time_of_delivery = models.DateTimeField()
    delivered_by = models.ForeignKey(User)
    successful = models.BooleanField(blank=True, default=False)

    @classmethod
    def begin(cls, assignment_group, user_obj):
        d = Delivery()
        d.assignment_group = assignment_group
        d.time_of_delivery = datetime.now()
        d.delivered_by = user_obj
        d.successful = False
        d.save()
        return d

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
    def where_is_student(cls, user_obj):
        return Delivery.objects.filter(assignment_group__students=user_obj,
                successful=True)

    @classmethod
    def where_is_examiner(cls, user_obj):
        return Delivery.objects.filter(assignment_group__examiners=user_obj,
                successful=True)

    def __unicode__(self):
        return u'%s %s' % (self.assignment_group, self.time_of_delivery)

    def finish(self):
        self.time_of_delivery = datetime.now()
        self.successful = True
        self.save()


    def add_file(self, filename, iterable_data):
        filemeta = FileMeta()
        filemeta.delivery = self
        filemeta.filename = filename
        filemeta.size = 0
        filemeta.save()
        f = FileMeta.store.write_open(filemeta)
        filemeta.save()
        for data in iterable_data:
            f.write(data)
            filemeta.size += len(data)
        f.close()
        filemeta.save()
        return filemeta



class Feedback(models.Model):
    """
    Represents the feedback for a given `Delivery`_.

    .. attribute:: grade

        A django.db.models.Charfield_ representing the grade given for the
        Delivery.

    .. attribute:: feedback_text

        A django.db.models.TextField_ that holds the feedback text given by
        the examiner.

    .. attribute:: feedback_format

        A django.db.models.CharField_ that holds the format of the feedback
        text.

    .. attribute:: feedback_published

        A django.db.models.BooleanField_ that tells if the feedback is
        published or not. This allows editing and saving the feedback before
        publishing it. Is useful for exams and other assignments when
        feedback and grading is published simultaneously for all Deliveries.

    .. attribute:: delivery

        A django.db.models.OneToOneField_ that points to the `Delivery`_ to
        be given feedback.

    """
    
    text_formats = (
       ('text', 'Text'),
       ('restructuredtext', 'ReStructured Text'),
       ('markdown', 'Markdown'),
       ('textile', 'Textile'),
    )
    feedback_text = models.TextField(blank=True, null=True, default='')
    feedback_format = models.CharField(max_length=20, choices=text_formats,
            default=text_formats[0])
    feedback_published = models.BooleanField(blank=True, default=False)
    delivery = models.OneToOneField(Delivery, blank=True, null=True)

    grade_type = models.ForeignKey(ContentType)
    grade_object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('grade_type', 'grade_object_id')

    def get_grade(self):
        return unicode(self.content_object)


class FileMeta(models.Model):
    delivery = models.ForeignKey(Delivery)
    filename = models.CharField(max_length=255)
    size = models.IntegerField()

    store = load_deliverystore_backend()


    def remove_file(self):
        return self.store.remove(self)

    def read_open(self):
        return self.store.read_open(self.delivery, self.filename)


def filemeta_deleted_handler(sender, **kwargs):
   filemeta = kwargs['instance']
   filemeta.remove_file()

from django.db.models.signals import pre_delete
pre_delete.connect(filemeta_deleted_handler, sender=FileMeta)
