# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

import binascii
import os

from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token

from devilry.devilry_account.models import User


def generate_key():
    return binascii.hexlify(os.urandom(20)).decode()


class APIKey(models.Model):
    """
    A class representing a given api key for a `user`.


    Extra stuff: when, where, who the key was last used.

    """
    class Meta:
        verbose_name = 'api key'
        verbose_name_plural = 'api keys'

    #: api key
    key = models.CharField(max_length=40, default=generate_key, unique=True, editable=False)

    #: The owner of the key
    user = models.ForeignKey(User, null=False, related_name='api_key')

    #: created timestamp
    created_datetime = models.DateTimeField(default=timezone.now)

    #: key activation start date
    start_datetime = models.DateTimeField(default=timezone.now)

    #: the key expire this date
    expiration_date = models.DateTimeField(blank=True, null=True)

    #: last login timestamp
    last_login_datetime = models.DateTimeField(blank=True, null=True)

    #: user agent
    user_agent = models.TextField(blank=True)

    def has_expired(self):
        """
        Checks if the :obj:`~.APIKey` has expired or not

        Returns:
            bool: true if the key has expired, false if not
        """
        return self.expiration_date <= timezone.now()

    def __str__(self):
        return '{} - {}'.format(self.user.shortname, self.key)
