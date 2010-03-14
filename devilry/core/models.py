from datetime import datetime
from django.db.models.signals import post_save, post_delete
from django.db import models
from django.contrib.auth.models import User, Permission
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from deliverystore import load_deliverystore_backend
import gradeplugin_registry



class BaseNode(models.Model):
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


    short_name = models.SlugField(max_length=20,
            verbose_name = _('Short name'),
            help_text=_("Max 20 characters. Only numbers, letters, '_' and '-'."))
    long_name = models.CharField(max_length=100,
            verbose_name='Long name',
            help_text=_('A longer name, more descriptive than "Short name".'))

    class Meta:
        abstract = True

    def get_path(self):
        return unicode(self)

    def admins_unicode(self):
        return u', '.join(u.username for u in self.admins.all())

    def is_admin(self, user_obj):
        """ Check if the given user is admin on this node or any parentnode.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: bool
        """
        if self.admins.filter(pk=user_obj.pk):
            return True
        elif self.parentnode:
            return self.parentnode.is_admin(user_obj)
        else:
            return False

    def can_save(self, user_obj):
        """ Check if the give user has permission to save this node.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: bool
        """
        if user_obj.is_superuser:
            return True
        if self.id == None:
            if self.__class__ == Node:
                return False
            # Must be admin on "parentnode" class to be permitted
            parentcls = self.__class__.parentnode.field.related.parent_model
            return parentcls.where_is_admin(user_obj).count() != 0
        elif self.is_admin(user_obj):
            return True
        else:
            return False


    @classmethod
    def where_is_admin(cls, user_obj):
        raise NotImplementedError()


class Node(BaseNode):
    """
    This class is typically used to represent a hierarchy of institutions, 
    faculties and departments. 

    .. attribute:: parentnode
        
        A django.db.models.ForeignKey_ that points to the parent node, which
        is always a `Node`_.

    .. attribute:: admins
        
        A django.db.models.ManyToManyField_ that holds all the admins of the `Node`_.
    """
    parentnode = models.ForeignKey('self', blank=True, null=True)
    admins = models.ManyToManyField(User, blank=True)

    class Meta:
        verbose_name = _('Node')
        verbose_name_plural = _('Nodes')


    def __unicode__(self):
        if self.parentnode:
            return unicode(self.parentnode) + "." + self.short_name
        else:
            return self.short_name


    def iter_childnodes(self):
        for node in self.node_set.all():
            yield node
            for c in node.iter_childnodes():
                yield c

    def clean(self, *args, **kwargs):
        if self.parentnode == None:
            q = Node.objects.filter(parentnode=None)
            if q.count() == 0:
                raise ValidationError('At least one node *must* be root.')
            else:
                if q.all()[0] != self:
                    raise ValidationError('Only one node can be the root node.')

        if self.parentnode == self:
            raise ValidationError('A node can not be it\'s own parent.')

        for node in self.iter_childnodes():
            if node == self.parentnode:
                raise ValidationError('A node can not be the child of one of it\'s own children.')


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
        """ Returns a QuerySet matching all Nodes where the given user is admin.
        
        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: QuerySet
        """
        return Node.objects.filter(pk__in=cls._get_nodepks_where_isadmin(user_obj))

    @classmethod
    def _get_pathlist_kw(cls, pathlist):
        """ Used by get_by_pathlist() to create the required kwargs for
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
        """ Get node by path just like get_by_path(), the parameter
        is a list of node-names instead of a single string. Example:
        
            >>> uio = Node(short_name='uio', long_name='UiO')
            >>> uio.save()
            >>> ifi = Node(short_name='ifi', long_name='Ifi', parentnode=uio)
            >>> ifi.save()
            >>> ifi
            <Node: uio.ifi>
            >>> Node.get_by_pathlist(['uio', 'ifi'])
            <Node: uio.ifi>
        """
        return Node.objects.get(**cls._get_pathlist_kw(pathlist))

    @classmethod
    def get_by_path(cls, path):
        """ Get a node by path. Just like `get_by_pathlist`, but the path is a
        string where the node-names are separated with '.'. """
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
        """ Just like `get_by_pathlist`, but the path is a string where each `short_name`
        is separated by '.', instead of a list. """
        return cls.get_by_pathlist(path.split('.'))


class Subject(BaseNode):
    """
    This class represents a subject. This may be either a full course,
    or one part of a course, if it is divided into parallell courses.
    
    .. attribute:: parentnode
        
        A django.db.models.ForeignKey_ that points to the parent node,
        which is always a `Node`_.

    .. attribute:: admins
        
        A django.db.models.ManyToManyField_ that holds all the admins of the `Node`_.
    """
    
    
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



class Period(BaseNode):
    """
    A Period represents a period of time, for example a half-year term
    at a university. 

    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node,
        which is always a `Subject`_.

    .. attribute:: start_time

        A django.db.models.DateTimeField_ representing the starting time of the period.
    
    .. attribute:: end_time 

        A django.db.models.DateTimeField_ representing the ending time of the period.

    .. attribute:: admins
        
        A django.db.models.ManyToManyField_ that holds all the admins of the node.
    """
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
        return self.short_name

    def str(self):
        return self.short_name


class Assignment(BaseNode):
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

        A django.db.models.DateTimeField_ representing the deadline of the assignment.

    .. attribute:: admins
        
        A django.db.models.ManyToManyField_ that holds all the admins of the Node.

    .. attribute:: feedback_plugin

        A django.db.models.CharField_ that holds the current feedback plugin used.
    """

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
        return unicode(self.parentnode) + " - " + self.short_name

    @classmethod
    def where_is_examiner(cls, user_obj):
        return Assignment.objects.filter(
            assignmentgroup_set__examiners=user_obj
            ).distinct()

    def assignment_groups_where_is_examiner(self, user_obj):
        return self.assignmentgroup_set.filter(examiners=user_obj)
 



class Candidate(models.Model):
    
    #assignmentgroup = models.ForeignKey(AssignmentGroupr)
    student = models.OneToOneField(User, blank=True, related_name="students")
    candidate_id = models.CharField(max_length=10)

    def __unicode__(self):
        return unicode(self.student)


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
    #students = models.ManyToManyField(User, blank=True, related_name="students")
    students = models.ManyToManyField(Candidate, blank=True)
    #students = models.ManyToOneField(Candidate)
    examiners = models.ManyToManyField(User, blank=True, related_name="examiners")
    is_open = models.BooleanField(blank=True, default=True,
            help_text = _('If this is checked, the group can add deliveries.'))


    @classmethod
    def where_is_admin(cls, user_obj):
        """ Returns a QuerySet matching all AssignmentGroups where the given user is admin.
        
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
        return AssignmentGroup.objects.filter(students=user_obj)

    @classmethod
    def published_where_is_student(cls, user_obj):
        return cls.where_is_student(user_obj).filter(
                parentnode__publishing_time__lt = datetime.now())

    @classmethod
    def active_where_is_student(cls, user_obj):
        now = datetime.now()
        return cls.published_where_is_student(user_obj).filter(
                parentnode__parentnode__start_time__lt = now,
                parentnode__parentnode__end_time__gt = now)

    @classmethod
    def old_where_is_student(cls, user_obj):
        now = datetime.now()
        return cls.published_where_is_student(user_obj).filter(
                parentnode__parentnode__end_time__lt = now)


    @classmethod
    def where_is_examiner(cls, user_obj):
        return AssignmentGroup.objects.filter(examiners=user_obj)

    

    def __unicode__(self):
        return u'%s (%s)' % (self.parentnode.long_name,
                ', '.join([unicode(x) for x in self.students.all()]))
    
    def get_students(self):
        return u'%s' % (', '.join([unicode(x) for x in self.students.all()]))

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
                return qry.annotate(models.Max('time_of_delivery'))[0].feedback.grade




class Delivery(models.Model):
    """
    A class representing a given delivery from an `AssignmentGroup`_. In some cases,
    a group are allowed to hand in several deliveries per assignment.

    .. attribute:: assignment_group

        A django.db.models.ForeignKey_ pointing to the `AssignmentGroup`_ that
        handed in the Delivery.

    .. attribute:: time_of_delivery

        A django.db.models.DateTimeField_ that holds the date and time the Delivery
        was uploaded.

    .. attribute:: delivered_by

        A django.db.models.ForeignKey_ pointing to the user that uploaded the Delivery

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
        """ Returns a QuerySet matching all Deliveries where the given user is admin.
        
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



from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Feedback(models.Model):
    """
    Represents the feedback for a given `Delivery`_.

    .. attribute:: grade

        A django.db.models.Charfield_ representing the grade given for the Delivery.

    .. attribute:: feedback_text

        A django.db.models.TextField_ that holds the feedback text given by the examiner.

    .. attribute:: feedback_format

        A django.db.models.CharField_ that holds the format of the feedback text.

    .. attribute:: feedback_published

        A django.db.models.BooleanField_ that tells if the feedback is published or not. 
        This allows editing and saving the feedback before publishing it. Is useful for
        exams and other assignments when feedback and grading is published simultaneously
        for all Deliveries.

    .. attribute:: delivery

        A django.db.models.OneToOneField_ that points to the `Delivery`_ to be given
        feedback.

    """
    
    text_formats = (
       ('text', 'Text'),
       ('restructuredtext', 'ReStructured Text'),
       ('markdown', 'Markdown'),
       ('textile', 'Textile'),
    )
    feedback_text = models.TextField(blank=True, null=True, default='')
    feedback_format = models.CharField(max_length=20, choices=text_formats)
    feedback_published = models.BooleanField(blank=True, default=False)
    delivery = models.OneToOneField(Delivery, blank=True, null=True)

    grade_type = models.ForeignKey(ContentType)
    grade_object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('grade_type', 'grade_object_id')



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

