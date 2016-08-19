from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_api.group_comment.serializers.serializer_student import GroupCommentSerializerStudent
from devilry.devilry_api.group_comment.views.groupcomment_base import GroupCommentViewBase
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.student_permission import StudentPermissionAPIKey
from devilry.devilry_group.models import GroupComment


class GroupCommentViewStudent(GroupCommentViewBase):
    permission_classes = (StudentPermissionAPIKey, )
    api_key_permissions = (APIKey.STUDENT_PERMISSION_READ, APIKey.STUDENT_PERMISSION_WRITE)
    serializer_class = GroupCommentSerializerStudent

    def get_role_query_set(self):
        assignment_group_queryset = AssignmentGroup.objects.filter_student_has_access(user=self.request.user)
        return GroupComment.objects.filter(feedback_set__group=assignment_group_queryset,
                                           comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                           visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

    def get(self, request, *args, **kwargs):
        return super(GroupCommentViewStudent, self).get(request, *args, **kwargs)

    get.__doc__ = GroupCommentViewBase.get.__doc__
