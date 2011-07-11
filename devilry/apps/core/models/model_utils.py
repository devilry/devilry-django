"""
.. attribute:: pathsep

    Path separator used by node-paths. The value is ``'.'``, and it must not
    be changed.
"""

from datetime import datetime
import re

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, Max
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import ugettext as _
from django.utils.formats import date_format

from ..deliverystore import load_deliverystore_backend, FileNotFoundError
from .. import gradeplugin


# TODO: indexes
# TODO: short_name ignorecase match on save.

pathsep = '.' # path separator for Node-paths

def splitpath(path, expected_len=0):
    """ Split the path on :attr:`pathsep` and return the resulting list.
    Example:

    >>> splitpath('uio.ifi.matnat')
    ['uio', 'ifi', 'matnat']
    >>> splitpath('uio.ifi.matnat', expected_len=2)
    Traceback (most recent call last):
    ...
    ValueError: Path must have exactly 2 parts

    :param expected_len:
        Expected length of the resulting list. If the resulting list is not
        exactly the given length, ``ValueError`` is raised. If
        ``expected_len`` is 0 (default), no checking is done.
    """
    p = path.split(pathsep)
    if expected_len and len(p) != expected_len:
        raise ValueError('Path must have exactly %d parts' % expected_len)
    return p


class EtagMismatchException(Exception):
    def __init__(self, etag):
        self.etag = etag

class Etag(object):
    """
    This class adds a method to update the object with an etag,
    making sure it is up to date before saving.
    """
    def etag_update(self, etag):
        if self.etag != etag:
            raise EtagMismatchException(self.etag)
        super(self.__class__, self).save()
