
from devilry.apps.core.models.assignment_group import AssignmentGroup
from devilry.devilry_api.assignment_group.views.assignmentgroup_base import AssignmentGroupListViewBase
from devilry.devilry_api.permission.student_permission import StudentReadOnlyAPIKey
from devilry.devilry_api.assignment_group.serializers.serializers_student import AssignmentGroupModelSerializer


class AssignmentGroupListViewStudent(AssignmentGroupListViewBase):
    permission_classes = (StudentReadOnlyAPIKey, )
    serializer_class = AssignmentGroupModelSerializer

    def get_role_query_set(self):
        return AssignmentGroup.objects.filter_student_has_access(self.request.user)

    def get(self, request, *args, **kwargs):
        return super(AssignmentGroupListViewStudent, self).get(request, *args, **kwargs)

    get.__doc__ = AssignmentGroupListViewBase.get.__doc__
