from django.db import models
from django.utils import timezone


class TestModel(models.Model):
    testfield = models.CharField(verbose_name="Test Value", max_length=100)


class FilterTestModel(models.Model):
    mybooleanfield = models.BooleanField(default=False)
    mycharfield = models.CharField(null=True, blank=True, default="", max_length=255)
    mytextfield = models.TextField(null=False, blank=False, default="")
    myintnullfield = models.IntegerField(default=None, null=True, blank=True)
    mydatetimefield = models.DateTimeField(default=timezone.now)
    mynulldatetimefield = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"FilterTestModel(mycharfield={self.mycharfield!r}, mybooleanfield={self.mybooleanfield})"
