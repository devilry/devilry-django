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
