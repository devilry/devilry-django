from rest_framework.permissions import IsAuthenticated
from devilry.devilry_account.models import User


class IsStudent(IsAuthenticated):
    """
    Permission class for student.

    Ensures that the request.user is authenticated and is student.
    """

    def has_permission(self, request, view):
        return super(IsStudent, self).has_permission(request, view) and User.objects.user_is_student(request.user)


class IsExaminer(IsAuthenticated):
    """
    Permission class for examiner.

    Ensures that the request.user is authenticated and is examiner.
    """

    def has_permission(self, request, view):
        return super(IsExaminer, self).has_permission(request, view) and User.objects.user_is_examiner(request.user)
