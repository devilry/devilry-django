class CoreDaoError(Exception):
    """
    Superclass for core dao errors.
    """

class PermissionDeniedError(CoreDaoError):
    """
    Raised to signal permission denied.
    """

class NotPermittedToDeleteNonEmptyError(PermissionDeniedError):
    """
    Raised to signal that the used do not have permission to delete non-empty item.
    """