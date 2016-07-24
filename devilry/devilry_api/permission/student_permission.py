from devilry.devilry_api.models import APIKey

from devilry.devilry_api.permission.base_permission import BaseIsAuthenticatedAPIKey


class StudentReadOnlyAPIKey(BaseIsAuthenticatedAPIKey):
    """
    Permission for student read only

    Ensures that the request.user is authenticated,
    apiKey has student permission "read" and
    method is read only
    """

    read_only_methods = ('GET', 'HEAD', 'OPTIONS')

    def has_permission(self, request, view):
        apikey = self.get_apikey(request)
        return (
            super(StudentReadOnlyAPIKey, self).has_permission(request, view) and
            apikey and
            apikey.student_permission == APIKey.STUDENT_PERMISSION_READ and
            request.method in self.read_only_methods
        )
