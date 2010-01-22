from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class BaseNode(models.Model):
    name = models.CharField(max_length=20)
    displayname = models.CharField(max_length=100)
    admins = models.ManyToManyField(User)

    class Meta:
        abstract = True


class Node(BaseNode):
    parent = models.ForeignKey('self', blank=True, null=True)

    def __unicode__(self):
        if self.parent:
            return unicode(self.parent) + "." + self.name
        else:
            return self.name


class Subject(BaseNode):
    parent = models.ForeignKey(Node)

    def __unicode__(self):
        return unicode(self.parent) + "." + self.name


class Period(BaseNode):
    subject = models.ForeignKey(Subject)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __unicode__(self):
        return unicode(self.subject) + "." + self.name


class Assignment(BaseNode):
    period = models.ForeignKey(Subject)
    deadline = models.DateTimeField()

    def __unicode__(self):
        return unicode(self.period) + "." + self.name


class Delivery(models.Model):
    assignment = models.ForeignKey(Assignment)
    students = models.ManyToManyField(User, related_name="students")
    examiners = models.ManyToManyField(User, related_name="examiners")

    #def __unicode__(self):
    #    return unicode(self.period) + "." + self.name


class DeliveryCandidate(models.Model):
    delivery = models.ForeignKey(Delivery)
    time_of_delivery = models.DateTimeField()

    def get_path(self):
        return join(settings.DEVILRY_DELIVERY_PATH, str(self.id))


class FileMeta(models.Model):
    delivery_candidate = models.ForeignKey(DeliveryCandidate)
    filename = models.CharField(max_length=500)
