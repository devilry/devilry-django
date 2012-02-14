"""
Validate and type-convert input to RESTful methods.
"""

from functools import wraps
from datetime import datetime

from devilry.rest.error import RestError


class InvalidIndataError(RestError):
    """
    Invalid indata.
    """


def none_or_bool(value):
    """
    Validator for :func:`indata` that requires that the value is ``None`` or a
    ``bool``.
    """
    if value == None:
        return value
    elif not isinstance(value, bool):
        raise ValueError('Value is not a bool. It is: ' + str(type(value)))
    else:
        return value

def none_or_unicode(value):
    """
    Validator for :func:`indata` that requires that the value is ``None`` or a
    ``unicode`` string. It also accepts bytestrings, which it will try to
    decode as utf-8.
    """
    if value == None:
        return value
    if isinstance(value, unicode):
        return value
    elif isinstance(value, str):
        try:
            return unicode(value, 'utf-8')
        except UnicodeDecodeError, e:
            raise ValueError("Could not decode value as UTF-8 string. " + str(e))
    else:
        raise ValueError('Invalid type: ' + str(type(value)))


def isoformatted_datetime(value):
    """

    """
    try:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
    except TypeError, e:
        raise ValueError(str(e))


def indata(**indataspec):
    """
    Decorator that takes care of validating and type-converting indata for a RESTful method.

    Each key in ``indataspec`` is a parameter name, and each value is a
    function that raises ``ValueError`` if the given value is of the wrong
    type. The function may also try to convert the type of the given value.

    Example::

        from devilry.rest.restbase import RestBase

        def int_minusone_is_none(data):
            data = int(data)
            if data == -1:
                return None
            return data

        class MyRestInterface(RestBase):
            @indata(name=unicode, age=int, size=int_minusone_is_none)
            def post(self, name, age, size):
                pass
    """
    def dec(targetfunc):
        targetfunc.indataspec = indataspec

        @wraps(targetfunc)
        def wrapper(self, **kwargs):
            converted_kwargs = {}
            for paramname, convert in indataspec.iteritems():
                if paramname in kwargs:
                    value = kwargs[paramname]
                    try:
                        converted_value = convert(value)
                    except ValueError, e:
                        raise InvalidIndataError('Could not convert parameter "{0}" to correct type: {1}'.format(paramname,
                            convert.__name__))
                    else:
                        converted_kwargs[paramname] = converted_value
            return targetfunc(self, **converted_kwargs)

        return wrapper

    return dec
