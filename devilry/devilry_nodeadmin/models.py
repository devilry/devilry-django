from __future__ import unicode_literals

from builtins import object
from django.db import models
from django.utils.translation import ugettext_lazy as _
from future.utils import python_2_unicode_compatible

@python_2_unicode_compatible
class Page(models.Model):
    node_title = models.CharField(max_length=100, verbose_name='node_title')

    def __str__(self):
        return self.node_title

    class Meta(object):
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')