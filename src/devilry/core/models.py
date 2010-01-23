from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings




class BaseNode(models.Model):
    short_name = models.SlugField(max_length=20,
            help_text=u"Only numbers, letters, '_' and '-'.")
    long_name = models.CharField(max_length=100)

    class Meta:
        abstract = True



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
    assignment = models.ForeignKey(Assignment)
    students = models.ManyToManyField(User, blank=True, related_name="students",
            through=DeliveryStudent)
    examiners = models.ManyToManyField(User, blank=True, related_name="examiners",
            through=DeliveryExaminer)

    #def __unicode__(self):
    #    return unicode(self.period) + "." + self.short_name


class DeliveryCandidate(models.Model):
    delivery = models.ForeignKey(Delivery)
    time_of_delivery = models.DateTimeField()

    def get_path(self):
        return join(settings.DEVILRY_DELIVERY_PATH, str(self.id))


class FileMeta(models.Model):
    delivery_candidate = models.ForeignKey(DeliveryCandidate)
    filename = models.CharField(max_length=500)




#def add_permissions_to_users(sender, **kwargs):
    #print dir(Node.admins.field)
    ##for adm in sender.admins.all():
    ##    print adm
    #print type(sender.admins.field)



#post_save.connect(add_permissions_to_users, sender=Node)
