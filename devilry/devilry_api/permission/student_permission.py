from devilry.devilry_api.models import APIKey

from devilry.devilry_api.permission.base_permission import(
    BaseIsAuthenticatedAPIKey,
    READ_HTTP_METHODS,
    WRITE_HTTP_METHODS)


class BaseStudentPermissionAPIKey(BaseIsAuthenticatedAPIKey):
    required_student_permissions = []

    def has_permission(self, request, view):
        return (
            super(BaseStudentPermissionAPIKey, self).has_permission(request, view) and
            self.apikey.student_permission in self.required_student_permissions and
            request.method in self.http_allowed_methods
        )


class StudentReadOnlyAPIKey(BaseStudentPermissionAPIKey):
    """
    Permission for student read only

    Ensures that the request.user is authenticated,
    apiKey has student permission "read" and
    method allowed is read only
    """

    http_allowed_methods = READ_HTTP_METHODS
    required_student_permissions = [APIKey.STUDENT_PERMISSION_READ, APIKey.STUDENT_PERMISSION_WRITE]


class StudentWriteAPIKey(BaseStudentPermissionAPIKey):
    """
    Permission for student has write access

    Ensures that the request.user is authenticated,
    apikey has student permission "write" and
    method allowed is write
    """
    http_allowed_methods = WRITE_HTTP_METHODS
    required_student_permissions = [APIKey.STUDENT_PERMISSION_WRITE]
