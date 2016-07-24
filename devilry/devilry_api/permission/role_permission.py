from rest_framework.authentication import get_authorization_header
from rest_framework.permissions import IsAuthenticated

from devilry.devilry_api.models import APIKey


class BasePermission(IsAuthenticated):

    def get_apikey(self, request):
        """
        This returns the api key object for the request

        Returns:
            :obj: `~devilry_api.APIKey`
        """
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b'token':
            return None
        key = auth[1].decode()
        return APIKey.objects.get(key=key)


class IsStudent(BasePermission):
    """
    Permission class for student.

    Ensures that the request.user is authenticated and is student.
    """

    def has_permission(self, request, view):
        apikey = self.get_apikey(request)
        return super(IsStudent, self).has_permission(request, view) and apikey and apikey.has_student_permission


class IsExaminer(BasePermission):
    """
    Permission class for examiner.

    Ensures that the request.user is authenticated and is examiner.
    """

    def has_permission(self, request, view):
        apikey = self.get_apikey(request)
        return super(IsExaminer, self).has_permission(request, view) and apikey and apikey.has_examiner_permission
