from devilry.devilry_api.models import APIKey

from devilry.devilry_api.permission.base_permission import BaseIsAuthenticatedAPIKey

READ_HTTP_METHODS = ['GET', 'HEAD', 'OPTIONS']
WRITE_HTTP_METHODS = ['GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'DELETE', 'PATCH']


class BaseStudentPermissionAPIKey(BaseIsAuthenticatedAPIKey):
    required_student_permissions = []
    http_allowed_methods = []

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
    method is read only
    """

    http_allowed_methods = READ_HTTP_METHODS
    required_student_permissions = [APIKey.STUDENT_PERMISSION_READ, APIKey.STUDENT_PERMISSION_WRITE]


class StudentWriteAPIKey(BaseStudentPermissionAPIKey):
    http_allowed_methods = WRITE_HTTP_METHODS
    required_student_permissions = [APIKey.STUDENT_PERMISSION_WRITE]