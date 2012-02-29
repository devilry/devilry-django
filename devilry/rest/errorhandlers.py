"""
Error handlers are functions that take an exception object as parameter, and
returns a HTTP status code and error reponse data.
"""
from django.core.exceptions import ValidationError
from error import ClientErrorBase


def create_errordict(errormessages=[], fielderrors={}):
    """
    Returns ``dict(errormessages=errormessages, fielderrors=fielderrors)``.
    This is mainly a function to encourage uniform error return format from
    errorhandlers.

    :param errormessages:
        Should be a list of unicode error messages.
    :param fielderrors:
        Should be a dict with fieldnames as key and list of unicode error
        messages as value.
    """
    return dict(errormessages=errormessages, fielderrors=fielderrors)


def django_validationerror(error):
    """
    An error handler that checks if ``error`` is a
    :exc:`django.core.exceptions.ValidationError` object, and if that is the
    case, ``(400, create_errordict([unicode(error)]))`` is returned.
    """
    if error and isinstance(error, ValidationError):
        errordict = None
        if hasattr(error, 'message_dict'):
            message_dict = error.message_dict
            if '__all__' in message_dict:
                del message_dict['__all__']
            if message_dict:
                errordict = create_errordict(fielderrors=message_dict)
        if not errordict: # Note: this may happen if we have have a message_dict with only __all__
            errordict = create_errordict(errormessages=error.messages)
        return 400, errordict
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
