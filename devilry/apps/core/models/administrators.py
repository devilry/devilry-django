from django.db import models


class AbstractAdministrator(models.Model):
    class Meta:
        abstract = True

