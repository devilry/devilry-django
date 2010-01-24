from django.db.models.signals import post_save, post_delete
from django.db import models
from django.contrib.auth.models import User, Permission
from django.conf import settings



class BaseNode(models.Model):
    short_name = models.SlugField(max_length=20,
            help_text=u"Only numbers, letters, '_' and '-'.")
    long_name = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def get_path(self):
        return unicode(self)
    get_path.short_description = 'Path'



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
            >>> ifi = Node.get_by_pathlist(['uio, 'ifi'])
        """
        return Node.objects.get(**cls.get_pathlist_kw(pathlist))

    @classmethod
    def get_by_path(cls, path):
        """ Get a node by path. Example:
            >>> ifi = Node.get_by_path('uio.ifi')
        """
        return cls.get_by_pathlist(path.split('.'))



class SubjectAdministator(BaseNodeAdministator):
    node = models.ForeignKey('Subject')

class Subject(BaseNode):
    parent = models.ForeignKey(Node)
    admins = models.ManyToManyField(User, blank=True, through=SubjectAdministator)

    def __unicode__(self):
        return unicode(self.parent) + "." + self.short_name



class PeriodAdministator(BaseNodeAdministator):
    node = models.ForeignKey('Period')

class Period(BaseNode):
    subject = models.ForeignKey(Subject)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    admins = models.ManyToManyField(User, blank=True, through=PeriodAdministator)

    def __unicode__(self):
        return unicode(self.subject) + "." + self.short_name



class AssignmentAdministator(BaseNodeAdministator):
    node = models.ForeignKey('Assignment')

class Assignment(BaseNode):
    period = models.ForeignKey(Period)
    deadline = models.DateTimeField()
    admins = models.ManyToManyField(User, blank=True, through=AssignmentAdministator)

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

    def __unicode__(self):
        return '%s (%s)' % (self.assignment,
                ', '.join([unicode(x) for x in self.students.all()]))


class DeliveryCandidate(models.Model):
    delivery = models.ForeignKey(Delivery)
    time_of_delivery = models.DateTimeField()


class FileMeta(models.Model):
    delivery_candidate = models.ForeignKey(DeliveryCandidate)
    filename = models.CharField(max_length=500)
    filepath = models.FileField(upload_to="deliveries")





class PermissionsForUserHandler:
    def __init__(self, content_type_names=[], codenames=[], add=True):
        print content_type_names, codenames
        self.content_type_names = content_type_names
        self.codenames = codenames
        if add:
            self._action = self._add
        else:
            self._action = self._remove

    def _add(self, permission, instance):
        try:
            permission.user_set.get(username=instance.user.username)
        except User.DoesNotExist, e:
            permission.user_set.add(instance.user)
            print "Added", permission, "TO", instance.user

    def _remove(self, permission, instance):
        pass

    def __call__(self, sender, **kwargs):
        print "CALLED"
        if self._action == self._add and not kwargs.get('created'):
            return
        instance = kwargs['instance']
        for content_type_name in self.content_type_names:
            for codename in self.codenames:
                codename = codename="%s_%s" % (codename, content_type_name)
                permission = Permission.objects.get(
                        content_type__name = content_type_name,
                        codename = codename)
                self._action(permission, instance)



#
# Signal handlers
#

content_type_names = ['node', 'subject', 'period', 'assignment', 'delivery']
node_post_save_handler = PermissionsForUserHandler(
        content_type_names, settings.DEVILRY_ADMIN_AUTOPERMISSIONS)
node_post_delete_handler = PermissionsForUserHandler(
        content_type_names, settings.DEVILRY_ADMIN_AUTOPERMISSIONS, add=False)
post_save.connect(node_post_save_handler, sender=NodeAdministator)
post_delete.connect(node_post_delete_handler, sender=NodeAdministator)

subject_post_save_handler = PermissionsForUserHandler(
        content_type_names[1:], settings.DEVILRY_ADMIN_AUTOPERMISSIONS)
subject_post_delete_handler = PermissionsForUserHandler(
        content_type_names[1:], settings.DEVILRY_ADMIN_AUTOPERMISSIONS, add=False)
post_save.connect(subject_post_save_handler, sender=SubjectAdministator)
post_delete.connect(subject_post_delete_handler, sender=SubjectAdministator)

period_post_save_handler = PermissionsForUserHandler(
        content_type_names[2:], settings.DEVILRY_ADMIN_AUTOPERMISSIONS)
period_post_delete_handler = PermissionsForUserHandler(
        content_type_names[2:], settings.DEVILRY_ADMIN_AUTOPERMISSIONS, add=False)
post_save.connect(period_post_save_handler, sender=PeriodAdministator)
post_delete.connect(period_post_delete_handler, sender=PeriodAdministator)

assignment_post_save_handler = PermissionsForUserHandler(
        content_type_names[3:], settings.DEVILRY_ADMIN_AUTOPERMISSIONS)
assignment_post_delete_handler = PermissionsForUserHandler(
        content_type_names[3:], settings.DEVILRY_ADMIN_AUTOPERMISSIONS, add=False)
post_save.connect(assignment_post_save_handler, sender=AssignmentAdministator)
post_delete.connect(assignment_post_delete_handler, sender=AssignmentAdministator)
