"""
Error handlers are functions that take an exception object as parameter, and
returns a HTTP status code and error reponse data.
"""
from django.core.exceptions import ValidationError
from error import ClientErrorBase


def create_errordict(errormessages=[], fielderrrors={}):
    """
    Returns ``dict(errormessages=errormessages, fielderrors=fielderrors)``.
    This is mainly a function to encourage uniform error return format from
    errorhandlers.

    :param errormessages:
        Should be a list of unicode error messages.
    :param fielderrrors:
        Should be a dict with fieldnames as key and list of unicode error
        messages as value.
    """
    return dict(errormessages=errormessages, fielderrrors=fielderrrors)


def django_validationerror(error):
    """
    An error handler that checks if ``error`` is a
    :exc:`django.core.exceptions.ValidationError` object, and if that is the
    case, ``(400, create_errordict([unicode(error)]))`` is returned.
    """
    if error and isinstance(error, ValidationError):
        return 400, create_errordict([unicode(error)])
    else:
        return None, None


def clienterror(error):
    """
    An error handler that checks if ``error`` is a
    :exc:`.error.ClientErrorBase` object, and if that is the case,
    ``(error.STATUS, create_errordict([unicode(error)]))`` is returned.
    """
    if error and isinstance(error, ClientErrorBase):
        return error.STATUS, create_errordict([unicode(error)])
    else:
        return None, None
