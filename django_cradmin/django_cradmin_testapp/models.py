from django.db import models


class TstRole(models.Model):
    """
    Used by tests that require a role object.
    """


class SomeItem(models.Model):
    name = models.CharField(max_length=30, verbose_name="The name")
    somenumber = models.IntegerField(null=True, blank=True)
    text = models.TextField(blank=True, null=False, default="")

    def __str__(self):
        return self.name
