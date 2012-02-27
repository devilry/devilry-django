"""
Error handlers are functions that take an exception object as parameter, and
returns a HTTP status code and error reponse data.
"""
from django.core.exceptions import ValidationError
from error import ClientErrorBase


def create_errordict(error):
    """
    Returns ``dict(error=unicode(error))``.
    """
    return dict(error=unicode(error))


def django_validationerror(error):
    """
    An error handler that checks if ``error`` is a
    :exc:`django.core.exceptions.ValidationError` object, and if that is the
    case, ``(400, create_errordict(error))`` is returned.
    """
    if error and isinstance(error, ValidationError):
        return 400, create_errordict(error)
    else:
        return None, None


def clienterror(error):
    """
    An error handler that checks if ``error`` is a
    :exc:`.error.ClientErrorBase` object, and if that is the case,
    ``(error.STATUS, create_errordict(error))`` is returned.
    """
    if error and isinstance(error, ClientErrorBase):
        return error.STATUS, create_errordict(error)
    else:
        return None, None
