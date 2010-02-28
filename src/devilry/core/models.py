from django.db.models.signals import post_save, post_delete
from django.db import models
from django.contrib.auth.models import User, Permission
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError
from django import forms




class PermMixinForeignKey(models.ForeignKey):
    def formfield(self, user_obj=None, **kwargs):
        if user_obj == None:
            return models.query.EmptyQuerySet()
        db = kwargs.pop('using', None)
        qry = self.related.parent_model.get_changelist(user_obj)
        defaults = {
            'form_class': forms.ModelChoiceField,
            'queryset': qry,
            'to_field_name': self.rel.field_name,
        }
        defaults.update(kwargs)
        return super(models.ForeignKey, self).formfield(**defaults)


class PermMixin(object):
    @classmethod
    def get_changelist(cls, user_obj):
        raise NotImplementedError('get_changelist must be implemented in subclass.')

    @classmethod
    def has_obj_permission(cls, user_obj, perm, obj):
        """ Check permissions for user on the given object of this model. """
        raise NotImplementedError('has_obj_permission must be implemented in subclass.')

    @classmethod
    def has_model_permission(cls, user_obj, perm):
        """
        Check permissions for user on this model. When object/instance
        permission is required, `has_obj_permission`_ is called instead.
        """
        if 'change_' in perm:
            return cls.get_changelist(user_obj).count() != 0
        return False


class CorePermMixin(PermMixin):
    @classmethod
    def get_changelist(cls, user_obj):
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

    @classmethod
    def has_obj_permission(cls, user_obj, perm, obj):
        if 'change_' in perm:
            return obj.is_admin(user_obj)
        elif obj.parentnode and 'delete_' in perm:
            return obj.parentnode.is_admin(user_obj)


class Node(BaseNode):
    parentnode = PermMixinForeignKey('self', blank=True, null=True)
    admins = models.ManyToManyField(User, blank=True)

    def __unicode__(self):
        if self.parentnode:
            return unicode(self.parentnode) + "." + self.short_name
        else:
            return self.short_name


    def clean(self, *args, **kwargs):
        if self.parentnode == self:
            raise ValidationError('A node can not be it\'s own parent.')
        super(Node, self).clean_fields(*args, **kwargs)

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
    parentnode = PermMixinForeignKey(Node)
    admins = models.ManyToManyField(User, blank=True)

    @classmethod
    def where_is_admin(cls, user_obj):
        return Subject.objects.filter(
                Q(admins__pk=user_obj.pk)
                | Q(parentnode__pk__in=Node.get_nodepks_where_isadmin(user_obj))).distinct()

    def __unicode__(self):
        return unicode(self.parentnode) + "." + self.short_name



class Period(BaseNode):
    parentnode = PermMixinForeignKey(Subject)
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
    parentnode = PermMixinForeignKey(Period)
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


class DeliveryGroup(models.Model, CorePermMixin):
    class Meta:
        verbose_name_plural = 'Delivery groups'
    parentnode = PermMixinForeignKey(Assignment)
    students = models.ManyToManyField(User, blank=True, related_name="students")
    examiners = models.ManyToManyField(User, blank=True, related_name="examiners")

    @classmethod
    def where_is_admin(cls, user_obj):
        return DeliveryGroup.objects.filter(
                Q(parentnode__admins=user_obj) |
                Q(parentnode__parentnode__admins=user_obj) |
                Q(parentnode__parentnode__parentnode__admins=user_obj) |
                Q(parentnode__parentnode__parentnode__parentnode__pk__in=Node.get_nodepks_where_isadmin(user_obj))
        ).distinct()

    @classmethod
    def where_is_student(cls, user_obj):
        return DeliveryGroup.objects.filter(students=user_obj)

    @classmethod
    def where_is_examiner(cls, user_obj):
        return DeliveryGroup.objects.filter(examiners=user_obj)

    def __unicode__(self):
        return u'%s (%s)' % (self.parentnode,
                ', '.join([unicode(x) for x in self.students.all()]))

    @classmethod
    def has_obj_permission(cls, user_obj, perm, obj):
        if 'change_' in perm:
            return obj.is_admin(user_obj)
        elif obj.parentnode and 'delete_' in perm:
            return obj.parentnode.is_admin(user_obj)

    def is_admin(self, user_obj):
        return self.parentnode.is_admin(user_obj)



class Delivery(models.Model, CorePermMixin):
    delivery_group = PermMixinForeignKey(DeliveryGroup)
    time_of_delivery = models.DateTimeField()

    @classmethod
    def where_is_admin(cls, user_obj):
        return Delivery.objects.filter(
                Q(delivery_group__parentnode__admins=user_obj) |
                Q(delivery_group__parentnode__parentnode__admins=user_obj) |
                Q(delivery_group__parentnode__parentnode__parentnode__admins=user_obj) |
                Q(delivery_group__parentnode__parentnode__parentnode__parentnode__pk__in=Node.get_nodepks_where_isadmin(user_obj))
        ).distinct()

    @classmethod
    def where_is_student(cls, user_obj):
        return Delivery.objects.filter(delivery_group__students=user_obj)

    @classmethod
    def where_is_examiner(cls, user_obj):
        return Delivery.objects.filter(delivery_group__examiners=user_obj)

    def __unicode__(self):
        return u'%s %s' % (self.delivery_group, self.time_of_delivery)


class FileMeta(models.Model, CorePermMixin):
    delivery = PermMixinForeignKey(Delivery)
    filepath = models.FileField(upload_to="deliveries")

    @classmethod
    def where_is_admin(cls, user_obj):
        return FileMeta.objects.filter(
                Q(delivery__delivery_group__parentnode__admins=user_obj) |
                Q(delivery__delivery_group__parentnode__parentnode__admins=user_obj) |
                Q(delivery__delivery_group__parentnode__parentnode__parentnode__admins=user_obj) |
                Q(delivery__delivery_group__parentnode__parentnode__parentnode__parent__pk__in=Node.get_nodepks_where_isadmin(user_obj))
        ).distinct()

    @classmethod
    def where_is_student(cls, user_obj):
        return FileMeta.objects.filter(delivery_group__delivery__students=user_obj)

    @classmethod
    def where_is_examiner(cls, user_obj):
        return FileMeta.objects.filter(delivery_group__delivery__examiners=user_obj)
