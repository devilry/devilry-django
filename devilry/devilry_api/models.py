# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

import binascii
import os

from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token
from django.utils.translation import pgettext_lazy, ugettext_lazy

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

    #: api key.
    key = models.CharField(max_length=40, default=generate_key, unique=True, editable=False)

    #: The owner of the key.
    user = models.ForeignKey(User, null=False, related_name='api_key')

    #: created timestamp.
    created_datetime = models.DateTimeField(default=timezone.now)

    #: the key expire this date or never if None.
    expiration_date = models.DateTimeField(blank=True, null=True)

    #: last login timestamp.
    last_login_datetime = models.DateTimeField(blank=True, null=True)

    #: user agent.
    user_agent = models.TextField(blank=True)

    #: purpose of the key
    purpose = models.CharField(max_length=255, blank=True)

    #: Constant for the :obj:`~.APIKey.role` "student" choice.
    ROLE_STUDENT = 'student'

    #: Constant for the :obj:`~.APIKey.role` "examiner" choice.
    ROLE_EXAMINER = 'examiner'

    #: Constant for the :obj:`~.APIKey.role` "admin" choice.
    ROLE_ADMIN = 'admin'

    #: Choices for :obj:`.APIKey.role'.
    ROLE_CHOICES = [
        (
            ROLE_STUDENT,
            pgettext_lazy('api key as role', 'student')
        ),
        (
            ROLE_EXAMINER,
            pgettext_lazy('api key as role', 'examiner')
        ),
        (
            ROLE_ADMIN,
            pgettext_lazy('api key as role', 'admin')
        )
    ]

    #: A choicefield for the api key role.
    #:
    #: Choices:
    #:
    #: - :obj:`~.APIKey.ROLE_STUDENT`
    #: - :obj:`~.APIKey.ROLE_EXAMINER`
    #: - :obj:`~.APIKey.ROLE_ADMIN`
    role = models.CharField(
        verbose_name=ugettext_lazy('api key role'),
        choices=ROLE_CHOICES,
        default=ROLE_STUDENT,
        max_length=255
    )

    #: Constant for the :obj: `~.APIKey.privilege` "read only" choice.
    PRIVILEGE_READ_ONLY = 'read only'

    #: Constant for the :obj: `~.APIKey.privilege` "all" choice.
    PRIVILEGE_ALL = 'all'

    #: Choices for :obj:`.APIKey.privilege'.
    PRIVILEGE_CHOICES = [
        (
            PRIVILEGE_READ_ONLY,
            pgettext_lazy('api key has privilege', 'read only')
        ),
        (
            PRIVILEGE_ALL,
            pgettext_lazy('api key has privilege', 'all')
        )
    ]

    #: A choicefield for the api key privilege.
    #:
    #: Choices:
    #:
    #: - :obj:`~.APIKey.PRIVILEGE_READ_ONLY`
    #: - :obj:`~.APIKey.PRIVILEGE_ALL`
    privilege = models.CharField(
        verbose_name=ugettext_lazy('api key privilege'),
        choices=PRIVILEGE_CHOICES,
        default=PRIVILEGE_READ_ONLY,
        max_length=255
    )

    #: Constant for the :obj: `~.APIKey.type` "half a year" choice.
    TYPE_SHORT_LIFETIME = 'half a year'

    #: Constant for the :obj: `~.APIKey.type` "a year" choice.
    TYPE_LONG_LIFETIME = 'a year'

    #: Choices for :obj:`.APIKey.type'.
    TYPE_CHOICES = [
        (
            TYPE_SHORT_LIFETIME,
            pgettext_lazy('api key lifetime', 'half a year')
        ),
        (
            TYPE_LONG_LIFETIME,
            pgettext_lazy('api key lifetime', 'a year')
        )
    ]

    #: A choicefield for the api key type.
    #:
    #: Choices:
    #:
    #: - :obj:`~.APIKey.TYPE_SHORT_LIFETIME`
    #: - :obj:`~.APIKey.TYPE_LONG_LIFETIME`
    type = models.CharField(
        verbose_name=ugettext_lazy('api key lifetime'),
        choices=TYPE_CHOICES,
        default=TYPE_SHORT_LIFETIME,
        max_length=255
    )

    @property
    def role_is_student(self):
        """
        This returns ``True`` if the :obj:`.APIKey.role` is student
        """
        return self.role == self.ROLE_STUDENT

    @property
    def role_is_examiner(self):
        """
        This returns ``True`` if the :obj:`.APIKey.role` is examiner
        """
        return self.role == self.ROLE_EXAMINER

    @property
    def role_is_admin(self):
        """
        This returns ``True`` if the :obj:`.APIKey.role` is admin
        """
        return self.role == self.ROLE_ADMIN

    @property
    def has_expired(self):
        """
        Checks if the :obj:`~.APIKey` has expired or not
        returns ``True`` if the key has expired
        """
        if self.expiration_date and self.expiration_date <= timezone.now():
            return True
        return False

    # @property
    # def is_active(self):
    #     """
    #     Checks if the :obj:`~.APIKey` is active
    #
    #     Returns:
    #         bool: true if the key is active, false if not
    #
    #     """
    #     if self.expiration_date is None and self.start_datetime <= timezone.now():
    #         return True
    #     elif self.start_datetime <= timezone.now() and self.expiration_date > timezone.now():
    #         return True
    #     else:
    #         return False

    def __str__(self):
        return '{} - {}'.format(self.user.shortname, self.key)
