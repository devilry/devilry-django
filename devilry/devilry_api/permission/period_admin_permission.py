from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.base_permission import (
    BaseIsAuthenticatedAPIKey,
    READ_HTTP_METHODS,
    WRITE_HTTP_METHODS
)

API_KEY_ALLOWED_METHODS = {
    APIKey.ADMIN_PERMISSION_READ: READ_HTTP_METHODS,
    APIKey.ADMIN_PERMISSION_WRITE: WRITE_HTTP_METHODS
}


class PeriodAdminPermissionAPIKey(BaseIsAuthenticatedAPIKey):
    """
    Permission for period admin
    """

    def has_permission(self, request, view):
        return (
            super(PeriodAdminPermissionAPIKey, self).has_permission(request, view) and
            self.apikey.admin_permission in view.api_key_permissions and
            request.method in API_KEY_ALLOWED_METHODS[self.apikey.admin_permission]
        )
