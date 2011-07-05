from django.db import models
from django.contrib.auth.models import User

from devilry.apps.core.models.period import Period


class StatConfig(models.Model):
    name = models.CharField(max_length=200)
    period = models.ForeignKey(Period)
    user = models.ForeignKey(User)
