from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django.db import models

import re

class ShortNameField(models.SlugField):
    """ Short name field used by several of the core models.

    We have a hierarchy of objects with a short name, but they are not
    strictly equal (eg. we cannot use a superclass because Subject has a
    unique short_name).
    """
    patt = re.compile(r'^[a-z0-9_-]+$')
    def __init__(self, *args, **kwargs):
        kw = dict(
            max_length = 20,
            verbose_name = _('Short name'),
            db_index = True,
            help_text=_(
                "Max 20 characters. Only numbers, lowercase characters, '_' " \
                    "and '-'. " ))
        kw.update(kwargs)
        super(ShortNameField, self).__init__(*args, **kw)

    def validate(self, value, *args, **kwargs):
        super(ShortNameField, self).validate(value, *args, **kwargs)
        if not self.patt.match(value):
            raise ValidationError(_(
                "Can only contain numbers, lowercase letters, '_' and '-'. "))


class LongNameField(models.CharField):
    def __init__(self, *args, **kwargs):
        kw = dict(max_length=100,
            verbose_name='Long name',
            db_index = True,
            help_text=_(
                'A longer name, more descriptive than "Short name". '\
                'This is the name visible to students.'))
        kw.update(kwargs)
        super(LongNameField, self).__init__(*args, **kw)
