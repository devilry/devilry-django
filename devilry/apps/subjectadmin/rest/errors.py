"""
Exceptions for ``devilry.apps.subjectadmin.rest``.
"""

class PermissionDeniedError(Exception):
    """
    Raised to signal permission denied.
    """

class NotPermittedToDeleteNonEmptyError(PermissionDeniedError):
    """
    Raised to signal that the used do not have permission to delete non-empty item.
    """
