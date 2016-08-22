from rest_framework.generics import mixins

from devilry.devilry_api.group_comment.serializers.serializer_examiner import GroupCommentSerializerExaminer
from devilry.devilry_api.group_comment.views.groupcomment_base import GroupCommentViewBase
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.examiner_permission import ExaminerPermissionAPIKey
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.models import GroupComment


class GroupCommentViewExaminer(mixins.CreateModelMixin,
                               GroupCommentViewBase):
    permission_classes = (ExaminerPermissionAPIKey, )
    api_key_permissions = (APIKey.EXAMINER_PERMISSION_READ, APIKey.EXAMINER_PERMISSION_WRITE)
    serializer_class = GroupCommentSerializerExaminer

    def get_role_query_set(self):
        assignment_group_queryset = AssignmentGroup.objects.filter_examiner_has_access(user=self.request.user)
        return GroupComment.objects.filter(feedback_set__group=assignment_group_queryset,
                                           comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT) \
            .exclude_private_comments_from_other_users(user=self.request.user)

    def get(self, request, feedback_set, *args, **kwargs):
        return super(GroupCommentViewExaminer, self).get(request, feedback_set, *args, **kwargs)

    get.__doc__ = GroupCommentViewBase.get.__doc__

    def post(self, request, feedback_set, *args, **kwargs):
        """
        post a comment to a feedbackset

        ---
        parameters:
            - name: feedback_set
              required: true
              paramType: path
              type: Int
              description: feedbackset id
            - name: text
              paramType: form
              required: true
              type: String
              description: comment text
            - name: part_of_grading
              required: false
              paramType: form
              type: Boolean
              description: part of grading
            - name: visibility
              required: false
              paramType: form
              enum:
                - visible-to-everyone
                - visible-to-examiner-and-admins
                - private
              description: comment visibility
        """
        request.data['feedback_set'] = feedback_set
        request.data['user_role'] = GroupComment.USER_ROLE_EXAMINER
        return super(GroupCommentViewExaminer, self).create(request, *args, **kwargs)