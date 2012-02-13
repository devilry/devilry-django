"""
Validate and type-convert input to RESTful methods.
"""

from functools import wraps
from devilry.rest.error import RestError


class InvalidIndataError(RestError):
    """
    Invalid indata.
    """

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
