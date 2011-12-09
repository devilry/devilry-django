from functools import wraps
from devilry.rest.error import RestError


class InvalidIndataError(RestError):
    """
    Invalid indata.
    """

def indata(**indataspec):
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