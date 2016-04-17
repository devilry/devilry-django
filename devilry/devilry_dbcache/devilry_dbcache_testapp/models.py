from django.db import models

from devilry.devilry_dbcache.bulk_create_queryset_mixin import BulkCreateQuerySetMixin


class PersonQuerySet(models.QuerySet, BulkCreateQuerySetMixin):
    pass


class Person(models.Model):
    objects = PersonQuerySet.as_manager()

    name = models.TextField()
    age = models.IntegerField(default=20)
