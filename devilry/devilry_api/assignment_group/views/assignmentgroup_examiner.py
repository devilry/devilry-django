from devilry.apps.core.models.assignment_group import AssignmentGroup
from devilry.devilry_api.assignment_group.serializers.serializers_examiner import AssignmentGroupModelSerializer
from devilry.devilry_api.assignment_group.views.assignmentgroup_base import AssignmentGroupListViewBase
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.examiner_permission import ExaminerPermissionAPIKey


class AssignmentGroupListViewExaminer(AssignmentGroupListViewBase):
    permission_classes = (ExaminerPermissionAPIKey, )
    serializer_class = AssignmentGroupModelSerializer
    api_key_permissions = (APIKey.EXAMINER_PERMISSION_READ, APIKey.EXAMINER_PERMISSION_WRITE)

    def get_role_query_set(self):
        return AssignmentGroup.objects.filter_examiner_has_access(self.request.user)

    def get(self, request, *args, **kwargs):
        return super(AssignmentGroupListViewExaminer, self).get(request, *args, **kwargs)

    get.__doc__ = AssignmentGroupListViewBase.get.__doc__