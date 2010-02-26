from django.db.models.signals import post_save, post_delete
from django.db import models
from django.contrib.auth.models import User, Permission
from django.conf import settings
from django.db.models import Q



class SecureQuerySet(object):
    def __init__(self, qryset, model, permcheck_method, user_obj):
        self.qryset = qryset
        self.model = model
        self.user_obj = user_obj
        self.permcheck_method = permcheck_method

    def filter(self, *args, **kwargs):
        permcheck_method = getattr(self.model, self.permcheck_method)
        extraargs = permcheck_method(self.user_obj)
        extraargs.extend(args)
        return self.qryset.filter(*extraargs, **kwargs)



class SecureQuerySetFactory(object):
    def __init__(self, model, permcheck_method):
        self.qryset = models.query.QuerySet(model)
        self.model = model
        self.permcheck_method = permcheck_method

    def __call__(self, user_obj):
        return SecureQuerySet(self.qryset, self.model, self.permcheck_method, user_obj)


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
    def has_change_perm_on_any(cls, user_obj):
        return cls.objects.filter(admins=user_obj).count() > 0


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
    parent = models.ForeignKey('self', blank=True, null=True)
    admins = models.ManyToManyField(User, blank=True, through=NodeAdministator)

    def __unicode__(self):
        if self.parent:
            return unicode(self.parent) + "." + self.short_name
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
            key = 'parent__' + key
            print node_obj
            print dir(node_obj)
            node_obj = node_obj.parent
        return kw

    @classmethod
    def get_nodepks_where_isadmin(cls, user_obj):
        """ Recurse down info all childnodes of the nodes below the nodes
        where ``user_obj`` is parent, and return the primary key of all these
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
    def get_qryargs_where_isadmin(cls, user_obj):
        return [Q(pk__in=cls.get_nodepks_where_isadmin(user_obj))]

    @classmethod
    def get_pathlist_kw(cls, pathlist):
        """ Used by get_by_pathlist() to create the required kwargs for
        Node.objects.get(). Might be a starting point for more sophisticated
        queries including paths. """
        kw = {}
        key = 'short_name'
        for short_name in reversed(pathlist):
            kw[key] = short_name
            key = 'parent__' + key
        return kw

    @classmethod
    def get_by_pathlist(cls, pathlist):
        """ Get node by path just like get_by_path(), the parameter
        is a list of node-names instead of a single string. Example:
            >>> uio = Node(short_name='uio', long_name='UiO')
            >>> uio.save()
            >>> ifi = Node(short_name='ifi', long_name='Ifi', parent=uio)
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
                n = Node(short_name=short_name, long_name=short_name, parent=parent)
                n.save()
            parent = n
        return n



class SubjectAdministator(BaseNodeAdministator):
    node = models.ForeignKey('Subject')

class Subject(BaseNode):
    parent = models.ForeignKey(Node)
    admins = models.ManyToManyField(User, blank=True, through=SubjectAdministator)

    @classmethod
    def get_qryargs_where_isadmin(cls, user_obj):
        return [Q(admins=user_obj) | Q(parent__pk__in=Node.get_nodepks_where_isadmin(user_obj))]

    def __unicode__(self):
        return unicode(self.parent) + "." + self.short_name



class PeriodAdministator(BaseNodeAdministator):
    node = models.ForeignKey('Period')

class Period(BaseNode):
    subject = models.ForeignKey(Subject)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    admins = models.ManyToManyField(User, blank=True, through=PeriodAdministator)

    @classmethod
    def get_qryargs_where_isadmin(cls, user_obj):
        return [Q(admins=user_obj) |
                Q(subject__admins=user_obj) |
                Q(subject__parent__pk__in=Node.get_nodepks_where_isadmin(user_obj))]

    def __unicode__(self):
        return unicode(self.subject) + "." + self.short_name



class AssignmentAdministator(BaseNodeAdministator):
    node = models.ForeignKey('Assignment')

class Assignment(BaseNode):
    period = models.ForeignKey(Period)
    deadline = models.DateTimeField()
    admins = models.ManyToManyField(User, blank=True, through=AssignmentAdministator)

    @classmethod
    def get_qryargs_where_isadmin(cls, user_obj):
        return [Q(admins=user_obj) |
                Q(period__admins=user_obj) |
                Q(period__subject__admins=user_obj) |
                Q(period__subject__parent__pk__in=Node.get_nodepks_where_isadmin(user_obj))]

    def __unicode__(self):
        return unicode(self.period) + "." + self.short_name



class DeliveryStudent(models.Model):
    delivery = models.ForeignKey('Delivery')
    student = models.ForeignKey(User)

class DeliveryExaminer(models.Model):
    delivery = models.ForeignKey('Delivery')
    examiner = models.ForeignKey(User)

class Delivery(models.Model):
    class Meta:
        verbose_name_plural = 'deliveries'
    assignment = models.ForeignKey(Assignment)
    students = models.ManyToManyField(User, blank=True, related_name="students",
            through=DeliveryStudent)
    examiners = models.ManyToManyField(User, blank=True, related_name="examiners",
            through=DeliveryExaminer)

    @classmethod
    def get_qryargs_where_isadmin(cls, user_obj):
        return [Q(assignment__admins=user_obj) |
                Q(assignment__period__admins=user_obj) |
                Q(assignment__period__subject__admins=user_obj) |
                Q(assignment__period__subject__parent__pk__in=Node.get_nodepks_where_isadmin(user_obj))]

    @classmethod
    def get_qryargs_where_isstudent(cls, user_obj):
        return [Q(students=user_obj)]

    @classmethod
    def get_qryargs_where_isexaminer(cls, user_obj):
        return [Q(examiners=user_obj)]

    def __unicode__(self):
        return u'%s (%s)' % (self.assignment,
                ', '.join([unicode(x) for x in self.students.all()]))


class DeliveryCandidate(models.Model):
    delivery = models.ForeignKey(Delivery)
    time_of_delivery = models.DateTimeField()

    @classmethod
    def get_qryargs_where_isadmin(cls, user_obj):
        return [Q(delivery__assignment__admins=user_obj) |
                Q(delivery__assignment__period__admins=user_obj) |
                Q(delivery__assignment__period__subject__admins=user_obj) |
                Q(delivery__assignment__period__subject__parent__pk__in=Node.get_nodepks_where_isadmin(user_obj))]

    @classmethod
    def get_qryargs_where_isstudent(cls, user_obj):
        return [Q(delivery__students=user_obj)]

    @classmethod
    def get_qryargs_where_isexaminer(cls, user_obj):
        return [Q(delivery__examiners=user_obj)]

    def __unicode__(self):
        return u'%s %s' % (self.delivery, self.time_of_delivery)


class FileMeta(models.Model):
    delivery_candidate = models.ForeignKey(DeliveryCandidate)
    filepath = models.FileField(upload_to="deliveries")

    @classmethod
    def get_qryargs_where_isadmin(cls, user_obj):
        return [Q(delivery_candiate__delivery__assignment__admins=user_obj) |
                Q(delivery_candiate__delivery__assignment__period__admins=user_obj) |
                Q(delivery_candiate__delivery__assignment__period__subject__admins=user_obj) |
                Q(delivery_candiate__delivery__assignment__period__subject__parent__pk__in=Node.get_nodepks_where_isadmin(user_obj))]

    @classmethod
    def get_qryargs_where_isstudent(cls, user_obj):
        return [Q(delivery_candiate__delivery__students=user_obj)]

    @classmethod
    def get_qryargs_where_isexaminer(cls, user_obj):
        return [Q(delivery_candiate__delivery__examiners=user_obj)]




for cls in Node, Subject, Period, Assignment:
    cls.adminobjects = SecureQuerySetFactory(cls, 'get_qryargs_where_isadmin')
for cls in Delivery, DeliveryCandidate, FileMeta:
    cls.adminobjects = SecureQuerySetFactory(cls, 'get_qryargs_where_isadmin')
    cls.examinerobjects = SecureQuerySetFactory(cls, 'get_qryargs_where_isexaminer')
    cls.studentobjects = SecureQuerySetFactory(cls, 'get_qryargs_where_isstudent')
