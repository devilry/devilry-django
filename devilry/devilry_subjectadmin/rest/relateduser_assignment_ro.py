"""
Read only interface that allows assignment admins to list related users.
"""
from djangorestframework.views import ListModelView
from djangorestframework.permissions import IsAuthenticated

from devilry.apps.core.models import Assignment

from .auth import IsAssignmentAdmin
from devilry.devilry_subjectadmin.rest.relateduser import ListRelatedUsersRestMixin
from devilry.devilry_subjectadmin.rest.relateduser import RelatedStudentResource
from devilry.devilry_subjectadmin.rest.relateduser import RelatedExaminerResource



class IsAssignmentAdminAssignmentIdKwarg(IsAssignmentAdmin):
    ID_KWARG = 'assignment_id'


class ListRelatedUsersOnAssignmentMixin(ListRelatedUsersRestMixin):
    def get_period_id(self):
        assignment_id = self.kwargs['assignment_id']
        assignment = Assignment.objects.get(id=assignment_id)
        return assignment.parentnode_id


class ListRelatedStudentsOnAssignmentRest(ListRelatedUsersOnAssignmentMixin, ListModelView):
    """
    Read-only listing of related students on the period containing the given assignment
    (The ID of the assignment is the last segment of the URL). Requires admin
    permissions on the assignment.
    """
    resource = RelatedStudentResource
    permissions = (IsAuthenticated, IsAssignmentAdminAssignmentIdKwarg)


class ListRelatedExaminersOnAssignmentRest(ListRelatedUsersOnAssignmentMixin, ListModelView):
    """
    Read-only listing of related examiners on the period containing the given assignment
    (The ID of the assignment is the last segment of the URL). Requires admin
    permissions on the assignment.
    """
    resource = RelatedExaminerResource
    permissions = (IsAuthenticated, IsAssignmentAdminAssignmentIdKwarg)
