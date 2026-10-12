from django.conf import settings
from django.db import models


class Site(models.Model):
    name = models.CharField(max_length=100)
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="listfilterdemo_admins")


class Person(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    banned_datetime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
