import datetime

from django.db import models
from django.utils import timezone


class Member(models.Model):
    name = models.CharField(max_length=255)


class AutoFormTestModel(models.Model):
    datetimefield_with_default = models.DateTimeField(default=timezone.now)
    datetimefield_without_default = models.DateTimeField()
    datefield_with_default = models.DateTimeField(default=datetime.date.today)
    datefield_without_default = models.DateTimeField()
    filefield = models.FileField()
    imagefield = models.ImageField()
    members = models.ManyToManyField(Member, blank=True)

    def __str__(self):
        return f"MyModel#{self.id}"
