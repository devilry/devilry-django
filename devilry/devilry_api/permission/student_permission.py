from devilry.devilry_api.models import APIKey

from devilry.devilry_api.permission.base_permission import(
    BaseIsAuthenticatedAPIKey,
    READ_HTTP_METHODS,
    WRITE_HTTP_METHODS)

#: API key student permissions allowed methods
API_KEY_ALLOWED_METHODS = {
    APIKey.STUDENT_PERMISSION_READ: READ_HTTP_METHODS,
    APIKey.STUDENT_PERMISSION_WRITE: WRITE_HTTP_METHODS,

}


class StudentPermissionAPIKey(BaseIsAuthenticatedAPIKey):
    """

    """

    def has_permission(self, request, view):
        return (
            super(StudentPermissionAPIKey, self).has_permission(request, view) and
            self.apikey.student_permission in view.api_key_permissions and
            request.method in API_KEY_ALLOWED_METHODS[self.apikey.student_permission]
        )
