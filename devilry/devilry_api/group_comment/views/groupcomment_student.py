from rest_framework.generics import mixins
from rest_framework.response import Response
from rest_framework import status

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_api.group_comment.serializers.serializer_student import GroupCommentSerializerStudent
from devilry.devilry_api.group_comment.views.groupcomment_base import BaseGroupCommentView
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.student_permission import StudentPermissionAPIKey
from devilry.devilry_group.models import GroupComment


class GroupCommentViewStudent(mixins.CreateModelMixin,
                              BaseGroupCommentView):
    permission_classes = (StudentPermissionAPIKey, )
    api_key_permissions = (APIKey.STUDENT_PERMISSION_READ, APIKey.STUDENT_PERMISSION_WRITE)
    serializer_class = GroupCommentSerializerStudent

    def get_role_query_set(self):
        """
        Returns role queryset for student role

        Returns:
            :class:`~devilry_group.GroupComment` queryset
        """
        assignment_group_queryset = AssignmentGroup.objects.filter_student_has_access(user=self.request.user)
        return GroupComment.objects.filter(feedback_set__group__in=assignment_group_queryset,
                                           comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                           visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)\
            .select_related('feedback_set__group__parentnode', 'user')

    def get(self, request, feedback_set, *args, **kwargs):
        return super(GroupCommentViewStudent, self).get(request, feedback_set, *args, **kwargs)

    get.__doc__ = BaseGroupCommentView.get.__doc__

    def create(self, feedback_set, request, *args, **kwargs):
        data = dict(request.data)
        data['feedback_set'] = feedback_set
        data['user_role'] = GroupComment.USER_ROLE_STUDENT
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
              required: true
              paramType: form
              type: String
              description: comment text
        """
        return self.create(feedback_set, request, *args, **kwargs)
