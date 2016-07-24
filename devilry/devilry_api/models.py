# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

import binascii
import os

from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token
from django.utils.translation import pgettext_lazy, ugettext_lazy
from datetime import timedelta
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

    #: last login timestamp.
    last_login_datetime = models.DateTimeField(blank=True, null=True)

    #: user agent.
    user_agent = models.TextField(blank=True)

    #: purpose of the key
    purpose = models.CharField(max_length=255, blank=True)

    #: Constant for the :obj:`~.APIKey.student_permission` "read" choice.
    STUDENT_PERMISSION_READ = 'read'

    #: Constant for the :obj:`~.APIKey.student_permission` "write" choice.
    STUDENT_PERMISSION_WRITE = 'write'

    #: Constant for the :obj:`~.APIKey.student_permission` "no permission" choice.
    STUDENT_NO_PERMISSION = 'no permission'

    #: Choices for :obj:`.APIKey.student_permission'.
    STUDENT_PERMISSION_CHOICES = [
        (
            STUDENT_NO_PERMISSION,
            pgettext_lazy('student permission', 'no permission')
        ),
        (
            STUDENT_PERMISSION_READ,
            pgettext_lazy('student permission', 'read')
        ),
        (
            STUDENT_PERMISSION_WRITE,
            pgettext_lazy('student permission', 'write')
        )
    ]

    #: A choicefield for the api key student permission.
    #:
    #: Choices:
    #:
    #: - :obj:`~.APIKey.STUDENT_NO_PERMISSION`
    #: - :obj:`~.APIKey.STUDENT_PERMISSION_READ`
    #: - :obj:`~.APIKey.STUDENT_PERMISSION_WRITE`
    student_permission = models.CharField(
        verbose_name=ugettext_lazy('student permission'),
        choices=STUDENT_PERMISSION_CHOICES,
        default=STUDENT_NO_PERMISSION,
        max_length=255
    )

    #: Constant for the :obj:`~.APIKey.examiner_permission` "read" choice.
    EXAMINER_PERMISSION_READ = 'read'

    #: Constant for the :obj:`~.APIKey.examiner_permission` "write" choice.
    EXAMINER_PERMISSION_WRITE = 'write'

    #: Constant for the :obj:`~.APIKey.examiner_permission` "no permission" choice.
    EXAMINER_NO_PERMISSION = 'no permission'

    #: Choices for :obj:`.APIKey.examiner_permission'.
    EXAMINER_PERMISSION_CHOICES = [
        (
            EXAMINER_NO_PERMISSION,
            pgettext_lazy('examiner permission', 'no permission')
        ),
        (
            EXAMINER_PERMISSION_READ,
            pgettext_lazy('examiner permission', 'read')
        ),
        (
            EXAMINER_PERMISSION_WRITE,
            pgettext_lazy('examiner permission', 'write')
        )
    ]

    #: A choicefield for the api key examiner permission.
    #:
    #: Choices:
    #:
    #: - :obj:`~.APIKey.EXAMINER_NO_PERMISSION`
    #: - :obj:`~.APIKey.EXAMINER_PERMISSION_READ`
    #: - :obj:`~.APIKey.EXAMINER_PERMISSION_WRITE`
    examiner_permission = models.CharField(
        verbose_name=ugettext_lazy('examiner permission'),
        choices=EXAMINER_PERMISSION_CHOICES,
        default=EXAMINER_NO_PERMISSION,
        max_length=255
    )

    #: Constant for the :obj:`~.APIKey.admin_permission` "read" choice.
    ADMIN_PERMISSION_READ = 'read'

    #: Constant for the :obj:`~.APIKey.admin_permission` "write" choice.
    ADMIN_PERMISSION_WRITE = 'write'

    #: Constant for the :obj:`~.APIKey.admin_permission` "no permission" choice.
    ADMIN_NO_PERMISSION = 'no permission'

    #: Choices for :obj:`.APIKey.admin_permission'.
    ADMIN_PERMISSION_CHOICES = [
        (
            ADMIN_NO_PERMISSION,
            pgettext_lazy('admin permission', 'no permission')
        ),
        (
            ADMIN_PERMISSION_READ,
            pgettext_lazy('admin permission', 'read')
        ),
        (
            ADMIN_PERMISSION_WRITE,
            pgettext_lazy('admin permission', 'write')
        )
    ]

    #: A choicefield for the api key admin permission.
    #:
    #: Choices:
    #:
    #: - :obj:`~.APIKey.ADMIN_NO_PERMISSION`
    #: - :obj:`~.APIKey.ADMIN_PERMISSION_READ`
    #: - :obj:`~.APIKey.ADMIN_PERMISSION_WRITE`
    admin_permission = models.CharField(
        verbose_name=ugettext_lazy('admin permission'),
        choices=ADMIN_PERMISSION_CHOICES,
        default=ADMIN_NO_PERMISSION,
        max_length=255
    )

    #: Constant for the :obj: `~.APIKey.lifetime` "half a year" choice.
    LIFETIME_SHORT = 'half a year'

    #: Constant for the :obj: `~.APIKey.lifetime` "a year" choice.
    LIFETIME_LONG = 'a year'

    #: Choices for :obj:`.APIKey.lifetime'.
    LIFETIME_CHOICES = [
        (
            LIFETIME_SHORT,
            pgettext_lazy('api key lifetime', 'half a year')
        ),
        (
            LIFETIME_LONG,
            pgettext_lazy('api key lifetime', 'a year')
        )
    ]

    #: A choicefield for the api key lifetime.
    #:
    #: Choices:
    #:
    #: - :obj:`~.APIKey.LIFETIME_SHORT`
    #: - :obj:`~.APIKey.LIFETIME_LONG`
    lifetime = models.CharField(
        verbose_name=ugettext_lazy('api key lifetime'),
        choices=LIFETIME_CHOICES,
        default=LIFETIME_SHORT,
        max_length=255
    )

    @property
    def key_has_student_permission(self):
        """
        This returns ``True`` if the :obj:`.APIKey.student_permission` has permission
        """
        return self.student_permission != self.STUDENT_NO_PERMISSION

    @property
    def key_has_examiner_permission(self):
        """
        This returns ``True`` if the :obj:`.APIKey.examiner_permission` has permission
        """
        return self.examiner_permission != self.EXAMINER_NO_PERMISSION

    @property
    def key_has_examiner_permission(self):
        """
        This returns ``True`` if the :obj:`.APIKey.admin_permission` has permission
        """
        return self.admin_permission != self.ADMIN_NO_PERMISSION

    LIFETIME = {
        LIFETIME_SHORT: timedelta(days=183),
        LIFETIME_LONG: timedelta(days=365)
    }

    @property
    def has_expired(self):
        """
        Checks if the :obj:`~.APIKey` has expired or not
        returns ``True`` if the key has expired
        """
        if self.created_datetime + self.LIFETIME[self.lifetime] <= timezone.now():
            return True
        return False

    def __str__(self):
        return '{} - {}'.format(self.user.shortname, self.key)
