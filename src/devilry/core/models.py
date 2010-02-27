from django.db.models.signals import post_save, post_delete
from django.db import models
from django.contrib.auth.models import User, Permission
from django.conf import settings
from django.db.models import Q



class BaseNode(models.Model):
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

    @classmethod
    def admin_changelist_qryset(cls, user_obj):
        return cls.objects.filter(cls.qry_where_is_admin(user_obj))

    @classmethod
    def user_has_model_perm(cls, user_obj, perm):
        meta = cls._meta
        changeperm = '%s.%s' % (meta.app_label, meta.get_change_permission())
        if perm == changeperm and cls.admin_changelist_qryset(user_obj).count() > 0:
            return True

        pcls = cls.parentnode.field.related.parent_model
        if pcls.admin_changelist_qryset(user_obj).count() > 0:
            return True



class BaseNodeAdministator(models.Model):
    user = models.ForeignKey(User)

    class Meta:
        abstract = True
        unique_together = (('user', 'node'))

    def __unicode__(self):
        return self.node.short_name + " -- " + self.user.username



class NodeAdministator(BaseNodeAdministator):
    node = models.ForeignKey('Node')

class Node(BaseNode):
    parentnode = models.ForeignKey('self', blank=True, null=True)
    admins = models.ManyToManyField(User, blank=True, through=NodeAdministator)

    def __unicode__(self):
        if self.parentnode:
            return unicode(self.parentnode) + "." + self.short_name
        else:
            return self.short_name

    @classmethod
    def get_isadmin_kw(cls, node_obj, user_obj):
        """ Create keywords for a query checking if the given ``user_obj`` is
        admin on the given node. The query created recurses all the way up to the top
        of the node hierarchy. """
        kw = {}
        key = 'admins'
        while node_obj != None:
            kw[key] = user_obj
            key = 'parentnode__' + key
            node_obj = node_obj.parentnode
        return kw

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
    def qry_where_is_admin(cls, user_obj):
        return Q(pk__in=cls.get_nodepks_where_isadmin(user_obj))

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



class SubjectAdministator(BaseNodeAdministator):
    node = models.ForeignKey('Subject')

class Subject(BaseNode):
    parentnode = models.ForeignKey(Node)
    admins = models.ManyToManyField(User, blank=True, through=SubjectAdministator)

    @classmethod
    def qry_where_is_admin(cls, user_obj):
        return Q(Q(admins=user_obj) | Q(parentnode__pk__in=Node.get_nodepks_where_isadmin(user_obj)))

    def __unicode__(self):
        return unicode(self.parentnode) + "." + self.short_name



class PeriodAdministator(BaseNodeAdministator):
    node = models.ForeignKey('Period')

class Period(BaseNode):
    parentnode = models.ForeignKey(Subject)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    admins = models.ManyToManyField(User, blank=True, through=PeriodAdministator)


    @classmethod
    def qry_where_is_admin(cls, user_obj):
        return Q(Q(admins=user_obj) |
                Q(parentnode__admins=user_obj) |
                Q(parentnode__parentnode__pk__in=Node.get_nodepks_where_isadmin(user_obj)))

    def __unicode__(self):
        return unicode(self.parentnode) + "." + self.short_name



class AssignmentAdministator(BaseNodeAdministator):
    node = models.ForeignKey('Assignment')

class Assignment(BaseNode):
    parentnode = models.ForeignKey(Period)
    deadline = models.DateTimeField()
    admins = models.ManyToManyField(User, blank=True, through=AssignmentAdministator)

    @classmethod
    def qry_where_is_admin(cls, user_obj):
        return Q(Q(admins=user_obj) |
                Q(parentnode__admins=user_obj) |
                Q(parentnode__parentnode__admins=user_obj) |
                Q(parentnode__parentnode__parentnode__pk__in=Node.get_nodepks_where_isadmin(user_obj)))

    def __unicode__(self):
        return unicode(self.parentnode) + "." + self.short_name



class DeliveryStudent(models.Model):
    delivery = models.ForeignKey('Delivery')
    student = models.ForeignKey(User)

class DeliveryExaminer(models.Model):
    delivery = models.ForeignKey('Delivery')
    examiner = models.ForeignKey(User)

class Delivery(models.Model):
    class Meta:
        verbose_name_plural = 'deliveries'
    parentnode = models.ForeignKey(Assignment)
    students = models.ManyToManyField(User, blank=True, related_name="students",
            through=DeliveryStudent)
    examiners = models.ManyToManyField(User, blank=True, related_name="examiners",
            through=DeliveryExaminer)

    @classmethod
    def qry_where_is_admin(cls, user_obj):
        return Q(Q(parentnode__admins=user_obj) |
                Q(parentnode__parentnode__admins=user_obj) |
                Q(parentnode__parentnode__parentnode__admins=user_obj) |
                Q(parentnode__parentnode__parentnode__parentnode__pk__in=Node.get_nodepks_where_isadmin(user_obj)))

    @classmethod
    def qry_where_is_student(cls, user_obj):
        return Q(students=user_obj)

    @classmethod
    def qry_where_is_examiner(cls, user_obj):
        return Q(examiners=user_obj)

    def __unicode__(self):
        return u'%s (%s)' % (self.parentnode,
                ', '.join([unicode(x) for x in self.students.all()]))

    @classmethod
    def admin_changelist_qryset(cls, user_obj):
        return cls.objects.filter(cls.qry_where_is_admin(user_obj))

    @classmethod
    def user_has_model_perm(cls, user_obj, perm):
        return cls.admin_changelist_qryset(user_obj).count() > 0



class StudentExaminerMixin(object):
    @classmethod
    def admin_changelist_qryset(cls, user_obj):
        return cls.objects.filter(Q(
                cls.qry_where_is_student(user_obj)
                | cls.qry_where_is_examiner(user_obj)
                | cls.qry_where_is_admin(user_obj)))

    @classmethod
    def user_has_model_perm(cls, user_obj, perm):
        if cls.objects.filter(cls.qry_where_is_student(user_obj)).count() > 0:
            return perm.startswith('core.add_')

        qry = Q(cls.qry_where_is_examiner(user_obj) | cls.qry_where_is_admin(user_obj))
        if cls.objects.filter(qry).count() > 0:
            return perm.startswith('core.examin_')


class DeliveryCandidate(models.Model, StudentExaminerMixin):
    delivery = models.ForeignKey(Delivery)
    time_of_delivery = models.DateTimeField()

    @classmethod
    def qry_where_is_admin(cls, user_obj):
        return Q(Q(delivery__parentnode__admins=user_obj) |
                Q(delivery__parentnode__parentnode__admins=user_obj) |
                Q(delivery__parentnode__parentnode__parentnode__admins=user_obj) |
                Q(delivery__parentnode__parentnode__parentnode__parentnode__pk__in=Node.get_nodepks_where_isadmin(user_obj)))

    @classmethod
    def qry_where_is_student(cls, user_obj):
        return Q(delivery__students=user_obj)

    @classmethod
    def qry_where_is_examiner(cls, user_obj):
        return Q(delivery__examiners=user_obj)

    def __unicode__(self):
        return u'%s %s' % (self.delivery, self.time_of_delivery)


class FileMeta(models.Model, StudentExaminerMixin):
    delivery_candidate = models.ForeignKey(DeliveryCandidate)
    filepath = models.FileField(upload_to="deliveries")

    @classmethod
    def qry_where_is_admin(cls, user_obj):
        return Q(Q(delivery_candiate__delivery__parentnode__admins=user_obj) |
                Q(delivery_candiate__delivery__parentnode__parentnode__admins=user_obj) |
                Q(delivery_candiate__delivery__parentnode__parentnode__parentnode__admins=user_obj) |
                Q(delivery_candiate__delivery__parentnode__parentnode__parentnode__parent__pk__in=Node.get_nodepks_where_isadmin(user_obj)))

    @classmethod
    def qry_where_is_student(cls, user_obj):
        return Q(delivery_candiate__delivery__students=user_obj)

    @classmethod
    def qry_where_is_examiner(cls, user_obj):
        return Q(delivery_candiate__delivery__examiners=user_obj)
