from datetime import datetime
from django.db.models.signals import post_save, post_delete
from django.db import models
from django.contrib.auth.models import User, Permission
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError
from deliverystore import load_deliverystore_backend
from django.utils.translation import ugettext as _



class BaseNode(models.Model):
    """
    The base class of the Devilry hierarchy. Implements basic functionality
    used by the other Node classes. An instance of this class typically 
    represents the institution running Devilry, i.e. The University of Oslo

    .. attribute:: short_name

        A ``django.db.models.SlugField`` with max 20 characters. Only numbers,
        letters, '_' and '-'.

    .. attribute:: long_name

        A ``django.db.models.CharField`` with max 100 characters. Gives a longer 
        description than :attr:`short_name`
        

    .. _django.db.models.SlugField: http://docs.djangoproject.com/en/dev/ref/models/fields/#slugfield
    .. _django.db.models.CharField: http://docs.djangoproject.com/en/dev/ref/models/fields/#charfield

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
        if self.admins.filter(pk=user_obj.pk):
            return True
        elif self.parentnode:
            return self.parentnode.is_admin(user_obj)
        else:
            return False

    @classmethod
    def where_is_admin(cls, user_obj):
        """ Get all nodes where `user_obj` is admin. """
        raise NotImplementedError()


class Node(BaseNode):
    
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
    parentnode = models.ForeignKey(Node)
    admins = models.ManyToManyField(User, blank=True)

    @classmethod
    def where_is_admin(cls, user_obj):
        return Subject.objects.filter(
                Q(admins__pk=user_obj.pk)
                | Q(parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))).distinct()

    def __unicode__(self):
        return self.short_name



class Period(BaseNode):
    parentnode = models.ForeignKey(Subject)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    admins = models.ManyToManyField(User, blank=True)


    @classmethod
    def where_is_admin(cls, user_obj):
        return Period.objects.filter(
                Q(admins=user_obj) |
                Q(parentnode__admins=user_obj) |
                Q(parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))
        ).distinct()

    def __unicode__(self):
        return unicode(self.parentnode) + " - " + self.short_name

    def str(self):
        return str(self.parentnode) + " - " + self.short_name


class Assignment(BaseNode):
    parentnode = models.ForeignKey(Period)
    publishing_time = models.DateTimeField()
    deadline = models.DateTimeField()
    admins = models.ManyToManyField(User, blank=True)

    @classmethod
    def where_is_admin(cls, user_obj):
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
 


class AssignmentGroup(models.Model):
    parentnode = models.ForeignKey(Assignment)
    students = models.ManyToManyField(User, blank=True, related_name="students")
    examiners = models.ManyToManyField(User, blank=True, related_name="examiners")
    is_open = models.BooleanField(blank=True, default=True,
            help_text = _('If this is checked, the group can add deliveries.'))


    @classmethod
    def where_is_admin(cls, user_obj):
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
    def get_active(cls, user_obj):
        now = datetime.now()
        return cls.published_where_is_student(user_obj).filter(
                parentnode__parentnode__start_time__lt = now,
                parentnode__parentnode__end_time__gt = now)


    @classmethod
    def where_is_examiner(cls, user_obj):
        return AssignmentGroup.objects.filter(examiners=user_obj)

    

    def __unicode__(self):
        return u'%s (%s)' % (self.parentnode,
                ', '.join([unicode(x) for x in self.students.all()]))

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
                return qry.annotate(models.Max('time_of_delivery'))[0].feedback.grade





class Delivery(models.Model):
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
    text_formats = (
       ('text', 'Text'),
       ('restructuredtext', 'ReStructured Text'),
       ('markdown', 'Markdown'),
       ('textile', 'Textile'),
    )
    grade = models.CharField(max_length=20, blank=True, null=True)
    feedback_text = models.TextField(blank=True, null=True, default='')
    feedback_format = models.CharField(max_length=20, choices=text_formats)
    feedback_published = models.BooleanField(blank=True, default=False)
    delivery = models.OneToOneField(Delivery, blank=True, null=True)


class FileMeta(models.Model):
    delivery = models.ForeignKey(Delivery)
    filename = models.CharField(max_length=255)
    size = models.IntegerField()

    store = load_deliverystore_backend()


    def remove_file(self):
        return self.store.remove(self, filemeta_obj.filename)

    def read_open(self):
        return self.store.read_open(self.delivery, self.filename)


def filemeta_deleted_handler(sender, **kwargs):
   filemeta = kwargs['instance']
   filemeta.remove_file()

from django.db.models.signals import pre_delete
pre_delete.connect(filemeta_deleted_handler, sender=FileMeta)



