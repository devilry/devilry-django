from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.base_permission import(
    BaseIsAuthenticatedAPIKey,
    READ_HTTP_METHODS,
    WRITE_HTTP_METHODS)

#: API key examiner permissions allowed methods
API_KEY_ALLOWED_METHODS = {
    APIKey.EXAMINER_PERMISSION_READ: READ_HTTP_METHODS,
    APIKey.EXAMINER_PERMISSION_WRITE: WRITE_HTTP_METHODS,

}


class ExaminerPermissionAPIKey(BaseIsAuthenticatedAPIKey):
    """
    Permission for examiner
    """

    def has_permission(self, request, view):
        return (
            super(ExaminerPermissionAPIKey, self).has_permission(request, view) and
            self.apikey.examiner_permission in view.api_key_permissions and
            request.method in API_KEY_ALLOWED_METHODS[self.apikey.examiner_permission]
        )
