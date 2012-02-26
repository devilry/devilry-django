"""
Validate and type-convert input to RESTful methods.
"""

from functools import wraps
from datetime import datetime
from inspect import getargspec

from devilry.rest.error import RestError


class InvalidIndataError(RestError):
    """
    Invalid indata.
    """


def unicode_indata(value):
    """
    Validator for :func:`indata` that requires that the value is a ``unicode``
    string. It also accepts bytestrings, which it will try to decode as utf-8.
    """
    if isinstance(value, unicode):
        return value
    elif isinstance(value, str):
        try:
            return unicode(value, 'utf-8')
        except UnicodeDecodeError, e:
            raise ValueError("Could not decode value as UTF-8 string. " + str(e))
    else:
        raise ValueError('Invalid type: ' + str(type(value)))


def bool_indata(value):
    """
    Validator for :func:`indata` that requires that the value is a ``bool`` or
    a basestring matching ``true`` or ``false`` when lowercased.
    """
    if isinstance(value, bool):
        return value
    elif isinstance(value, basestring):
        value = value.lower()
        if value == 'true':
            return True
        elif value == 'false':
            return False
    raise ValueError('Invalid type: ' + str(type(value)))


def isoformatted_datetime(value):
    """
    Expects value to be a datetime string on the following format:
    ``"%Y-%m-%dT%H:%M:%S"``. Raises ``ValueError`` if it is not correctly
    formatted.
    """
    try:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
    except TypeError, e:
        raise ValueError(str(e))

class NoneOr(object):
    """
    Wraps any :func:`indata` validator with the ability to allow ``None`` as
    value. Example::

        >>> NoneOr(unicode)('Hello world')
        u'Hello world'
        >>> NoneOr(unicode)(None)
        None
    """
    def __init__(self, notnone_handler):
        self.notnone_handler = notnone_handler

    def __call__(self, value):
        if value == None:
            return None
        else:
            notnone_handler = self.notnone_handler
            return notnone_handler(value)


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
        argspec = getargspec(targetfunc)
        args = argspec[0]
        required_argcount = len(args)

        @wraps(targetfunc)
        def wrapper(self, **kwargs):
            if len(kwargs) != required_argcount:
                raise InvalidIndataError('{funcname}(...) takes {required_argcount} arguments '
                                         '({argcount} given).'.format(funcname=targetfunc.__name__,
                                                                      required_argcount=required_argcount,
                                                                      argcount=len(kwargs)))

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
