from rest_framework.permissions import IsAuthenticated


class IsStudent(IsAuthenticated):
    """
    Permission class for student.

    Ensures that the request.user is authenticated and is student.
    """

    def has_permission(self, request, view):
        return super(IsStudent, self).has_permission(request, view) and request.user.user_is_student()


class IsExaminer(IsAuthenticated):
    """
    Permission class for examiner.

    Ensures that the request.user is authenticated and is examiner.
    """

    def has_permission(self, request, view):
        return super(IsExaminer, self).has_permission(request, view) and request.user.user_is_examiner()
