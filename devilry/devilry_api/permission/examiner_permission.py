from devilry.devilry_api.models import APIKey

from devilry.devilry_api.permission.base_permission import(
    BaseIsAuthenticatedAPIKey,
    READ_HTTP_METHODS,
    WRITE_HTTP_METHODS)


class BaseExaminerPermissionAPIKey(BaseIsAuthenticatedAPIKey):
    required_examiner_permissions = []

    def has_permission(self, request, view):
        return (
            super(BaseExaminerPermissionAPIKey, self).has_permission(request, view) and
            self.apikey.examiner_permission in self.required_examiner_permissions and
            request.method in self.http_allowed_methods
        )


class ExaminerReadOnlyAPIKey(BaseExaminerPermissionAPIKey):
    """
    Permission for examiner has read only access

    Ensures that the request.user is authenticated,
    apiKey has student permission "read" and
    method allowed is read only
    """

    http_allowed_methods = READ_HTTP_METHODS
    required_examiner_permissions = [APIKey.EXAMINER_PERMISSION_READ, APIKey.EXAMINER_PERMISSION_WRITE]


class ExaminerWriteAPIKey(BaseExaminerPermissionAPIKey):
    """
    Permission for examiner has write access

    Ensures that the request.user is authenticated,
    apikey has student permission "write" and
    method allowed is write
    """
    http_allowed_methods = WRITE_HTTP_METHODS
    required_examiner_permissions = [APIKey.STUDENT_PERMISSION_WRITE]
