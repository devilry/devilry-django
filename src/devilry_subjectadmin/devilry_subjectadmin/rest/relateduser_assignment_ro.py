"""
Read only interface that allows assignment admins to list related users.
"""
from djangorestframework.views import ListModelView
from djangorestframework.permissions import IsAuthenticated

from devilry.apps.core.models import Assignment

from .auth import IsAssignmentAdmin
from .relateduser import ListRelatedUsersRestMixin
from .relateduser import RelatedStudentResource
from .relateduser import RelatedExaminerResource



class IsAssignmentAdminAssignmentIdKwarg(IsAssignmentAdmin):
    ID_KWARG = 'assignment_id'


class ListRelatedUsersOnAssignmentMixin(ListRelatedUsersRestMixin):
    def get_period_id(self):
        assignment_id = self.kwargs['assignment_id']
        assignment = Assignment.objects.get(id=assignment_id)
        return assignment.parentnode_id


class ListRelatedStudentsOnAssignmentRest(ListRelatedUsersOnAssignmentMixin, ListModelView):
    resource = RelatedStudentResource
    permissions = (IsAuthenticated, IsAssignmentAdminAssignmentIdKwarg)


class ListRelatedExaminersOnAssignmentRest(ListRelatedUsersOnAssignmentMixin, ListModelView):
    resource = RelatedExaminerResource
    permissions = (IsAuthenticated, IsAssignmentAdminAssignmentIdKwarg)
