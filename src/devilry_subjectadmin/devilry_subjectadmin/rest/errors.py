"""
Exceptions for ``devilry_subjectadmin.rest``.
"""

from djangorestframework.response import ErrorResponse
from djangorestframework import status



class PermissionDeniedError(ErrorResponse):
    """
    Raised to signal permission denied.
    """
    def __init__(self, errormsg):
        super(PermissionDeniedError, self).__init__(status.HTTP_403_FORBIDDEN,
                                                    {'detail': errormsg})

class BadRequestFieldError(ErrorResponse):
    """
    Raised to signal that a field has some error.
    """
    def __init__(self, field, errormsg):
        super(BadRequestFieldError, self).__init__(status.HTTP_400_BAD_REQUEST,
                                                   {'field_errors': {field: [errormsg]}})


class ValidationErrorResponse(ErrorResponse):
    """
    Should be raised when a :exc:`django.core.exceptions.ValidationError` is
    raised, to respond with an appropritate ErrorResponse.
    """
    def __init__(self, validationerror):
        message_dict = validationerror.message_dict
        messages = validationerror.messages
        if '__all__' in message_dict:
            del message_dict['__all__'] # We assume __all__ is duplicated in messages
        super(ValidationErrorResponse, self).__init__(status.HTTP_400_BAD_REQUEST,
                                                   {'field_errors': message_dict,
                                                    'errors': messages})
