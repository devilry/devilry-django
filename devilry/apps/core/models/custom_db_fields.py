import re

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import models


class ShortNameField(models.SlugField):
    """ Short name field used by several of the core models.

    We have a hierarchy of objects with a short name, but they are not
    strictly equal (eg. we cannot use a superclass because Subject has a
    unique short_name).
    """
    patt = re.compile(r'^[a-z0-9_-]+$')

    def __init__(self, *args, **kwargs):
        kw = dict(
            max_length=20,
            verbose_name=_('Short name'),
            db_index=True,
            help_text=_('Up to 20 letters of lowercase english letters (a-z), '
                        'numbers, underscore ("_") and hyphen ("-"). Used when the '
                        'name takes too much space.')
        )
        kw.update(kwargs)
        super(ShortNameField, self).__init__(*args, **kw)

    def validate(self, value, *args, **kwargs):
        super(ShortNameField, self).validate(value, *args, **kwargs)
        if not self.patt.match(value):
            raise ValidationError(_(
                "Can only contain numbers, lowercase letters, '_' and '-'. "))


class LongNameField(models.CharField):
    def __init__(self, *args, **kwargs):
        kw = dict(
            max_length=100,
            verbose_name=_('Name'),
            db_index=True)
        kw.update(kwargs)
        super(LongNameField, self).__init__(*args, **kw)
