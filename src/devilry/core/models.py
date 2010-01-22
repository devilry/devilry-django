from django.db import models


class DevilryUser(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField()

    def __unicode__(self):
        return self.name


class BaseNode(models.Model):
    name = models.CharField(max_length=20)
    displayname = models.CharField(max_length=100)
    admins = models.ManyToManyField(DevilryUser)

    class Meta:
        abstract = True

class Node(BaseNode):
    parent = models.ForeignKey('self', blank=True, null=True)

    def __unicode__(self):
        if self.parent:
            return unicode(self.parent) + "." + self.name
        else:
            return self.name


class SubjectNode(BaseNode):
    parent = models.ForeignKey(Node)

    def __unicode__(self):
        if self.parent:
            return unicode(self.parent) + "." + self.name
        else:
            return self.name


class PeriodNode(BaseNode):
    subject = models.ForeignKey(SubjectNode)
    students = models.ManyToManyField(DevilryUser, related_name="students")
    examiners = models.ManyToManyField(DevilryUser, related_name="examiners")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __unicode__(self):
        if self.subject:
            return unicode(self.subject) + "." + self.name
        else:
            return self.name


class AssignmentNode(BaseNode):
    period = models.ForeignKey(SubjectNode)
