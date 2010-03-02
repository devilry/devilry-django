from datetime import datetime
from django.db.models.signals import post_save, post_delete
from django.db import models
from django.contrib.auth.models import User, Permission
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError
from devilry.auth import authmodel
from deliverystore import load_deliverystore_backend



class CorePermMixin(authmodel.PermMixin):
    @classmethod
    def get_changelist(cls, user_obj):
        if user_obj.is_superuser:
            return cls.objects.all()
        else:
            return cls.where_is_admin(user_obj)


class BaseNode(models.Model, CorePermMixin):
    short_name = models.SlugField(max_length=20,
            help_text=u"Only numbers, letters, '_' and '-'.")
    long_name = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def get_path(self):
        return unicode(self)
    get_path.short_description = 'Path'

    def admins_unicode(self):
        return u', '.join(u.username for u in self.admins.all())
    admins_unicode.short_description = 'Admins'

    def is_admin(self, user_obj):
        if self.admins.filter(pk=user_obj.pk):
            return True
        elif self.parentnode:
            return self.parentnode.is_admin(user_obj)
        else:
            return False


class Node(BaseNode):
    parentnode = authmodel.ForeignKey('self', blank=True, null=True)
    admins = models.ManyToManyField(User, blank=True)

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
    def get_nodepks_where_isadmin(cls, user_obj):
        """ Recurse down info all childnodes of the nodes below the nodes
        where ``user_obj`` is admin, and return the primary key of all these
        nodes in a list. """
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
        return Node.objects.filter(pk__in=cls.get_nodepks_where_isadmin(user_obj))

    @classmethod
    def get_pathlist_kw(cls, pathlist):
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
        return Node.objects.get(**cls.get_pathlist_kw(pathlist))

    @classmethod
    def get_by_path(cls, path):
        """ Get a node by path. Just like get_by_pathlist(), but the path is a
        string where the node-names are separated with '.'. """
        return cls.get_by_pathlist(path.split('.'))


    @classmethod
    def create_by_pathlist(cls, pathlist):
        """ Create a new node by pathlist, creating all missing parents. """
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

class Subject(BaseNode):
    parentnode = authmodel.ForeignKey(Node)
    admins = models.ManyToManyField(User, blank=True)

    @classmethod
    def where_is_admin(cls, user_obj):
        return Subject.objects.filter(
                Q(admins__pk=user_obj.pk)
                | Q(parentnode__pk__in=Node.get_nodepks_where_isadmin(user_obj))).distinct()

    def __unicode__(self):
        return unicode(self.parentnode) + "." + self.short_name



class Period(BaseNode):
    parentnode = authmodel.ForeignKey(Subject)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    admins = models.ManyToManyField(User, blank=True)


    @classmethod
    def where_is_admin(cls, user_obj):
        return Period.objects.filter(
                Q(admins=user_obj) |
                Q(parentnode__admins=user_obj) |
                Q(parentnode__parentnode__pk__in=Node.get_nodepks_where_isadmin(user_obj))
        ).distinct()

    def __unicode__(self):
        return unicode(self.parentnode) + "." + self.short_name


class Assignment(BaseNode):
    parentnode = authmodel.ForeignKey(Period)
    deadline = models.DateTimeField()
    admins = models.ManyToManyField(User, blank=True)

    @classmethod
    def where_is_admin(cls, user_obj):
        return Assignment.objects.filter(
                Q(admins=user_obj) |
                Q(parentnode__admins=user_obj) |
                Q(parentnode__parentnode__admins=user_obj) |
                Q(parentnode__parentnode__parentnode__pk__in=Node.get_nodepks_where_isadmin(user_obj))
        ).distinct()

    def __unicode__(self):
        return unicode(self.parentnode) + "." + self.short_name


class AssignmentGroup(models.Model, CorePermMixin):
    class Meta:
        verbose_name_plural = 'Delivery groups'
    parentnode = authmodel.ForeignKey(Assignment)
    students = models.ManyToManyField(User, blank=True, related_name="students")
    examiners = models.ManyToManyField(User, blank=True, related_name="examiners")

    @classmethod
    def where_is_admin(cls, user_obj):
        return AssignmentGroup.objects.filter(
                Q(parentnode__admins=user_obj) |
                Q(parentnode__parentnode__admins=user_obj) |
                Q(parentnode__parentnode__parentnode__admins=user_obj) |
                Q(parentnode__parentnode__parentnode__parentnode__pk__in=Node.get_nodepks_where_isadmin(user_obj))
        ).distinct()

    @classmethod
    def where_is_student(cls, user_obj):
        return AssignmentGroup.objects.filter(students=user_obj)

    @classmethod
    def where_is_examiner(cls, user_obj):
        return AssignmentGroup.objects.filter(examiners=user_obj)

    def __unicode__(self):
        return u'%s (%s)' % (self.parentnode,
                ', '.join([unicode(x) for x in self.students.all()]))

    def is_admin(self, user_obj):
        return self.parentnode.is_admin(user_obj)

    def is_student(self, user_obj):
        return self.students.filter(id=user_obj.id).count() > 0



class Delivery(models.Model, CorePermMixin):
    assignment_group = authmodel.ForeignKey(AssignmentGroup)
    time_of_delivery = models.DateTimeField(null=True, default=None)
    store = load_deliverystore_backend()


    @classmethod
    def begin(cls, assignment_group):
        d = Delivery()
        d.assignment_group = assignment_group
        d.save()
        return d

    def finish(self):
        self.time_of_delivery = datetime.now()
        self.save()

    @classmethod
    def where_is_admin(cls, user_obj):
        return Delivery.objects.filter(
                Q(assignment_group__parentnode__admins=user_obj) |
                Q(assignment_group__parentnode__parentnode__admins=user_obj) |
                Q(assignment_group__parentnode__parentnode__parentnode__admins=user_obj) |
                Q(assignment_group__parentnode__parentnode__parentnode__parentnode__pk__in=Node.get_nodepks_where_isadmin(user_obj))
        ).distinct()

    @classmethod
    def where_is_student(cls, user_obj):
        return Delivery.objects.filter(assignment_group__students=user_obj)

    @classmethod
    def where_is_examiner(cls, user_obj):
        return Delivery.objects.filter(assignment_group__examiners=user_obj)

    def __unicode__(self):
        return u'%s %s' % (self.assignment_group, self.time_of_delivery)
