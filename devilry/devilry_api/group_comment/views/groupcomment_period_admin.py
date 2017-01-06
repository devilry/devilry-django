from rest_framework.generics import mixins
from rest_framework.response import Response
from rest_framework import status


from devilry.devilry_api.group_comment.views.groupcomment_base import BaseGroupCommentView
from devilry.devilry_api.permission.period_admin_permission import PeriodAdminPermissionAPIKey
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.group_comment.serializers.serializer_period_admin import GroupCommentSerializerPeriodAdmin
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.models import GroupComment


class GroupCommentViewPeriodAdmin(mixins.CreateModelMixin,
                                  BaseGroupCommentView):
    permission_classes = (PeriodAdminPermissionAPIKey, )
    api_key_permissions = (APIKey.ADMIN_PERMISSION_READ, APIKey.ADMIN_PERMISSION_WRITE)
    serializer_class = GroupCommentSerializerPeriodAdmin

    def get_role_query_set(self):
        """
        Returns role queryset for period admin role

        Returns:
            :class:`~devilry_group.GroupComment` queryset
        """
        assignment_group_queryset = AssignmentGroup.objects.filter_user_is_period_admin(user=self.request.user)
        return GroupComment.objects.filter(feedback_set__group__in=assignment_group_queryset,
                                           comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT)\
            .select_related('feedback_set__group')\
            .exclude_private_comments_from_other_users(user=self.request.user)

    def get(self, request, feedback_set, *args, **kwargs):
        return super(GroupCommentViewPeriodAdmin, self).get(request, feedback_set, *args, **kwargs)

    get.__doc__ = BaseGroupCommentView.get.__doc__

    def create(self, feedback_set, request, *args, **kwargs):
        """
        Creates a feedbackset
        Args:
            feedback_set: :attr:`~devilry_grup.FeedbackSet.id`
            request: request object

        Returns:
            Returns http 201 response or exception is raised
        """
        data = dict(request.data)
        data['feedback_set'] = feedback_set
        data['user_role'] = GroupComment.USER_ROLE_ADMIN
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def post(self, request, feedback_set, *args, **kwargs):
        """
        post a comment to a feedbackset.
        Period admin cannot post part of grading comments,
        only comments with visibility to everyone and examiner and admins.

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
            - name: visibility
              required: false
              paramType: form
              enum:
                - visible-to-everyone
                - visible-to-examiner-and-admins
              description: comment visibility
        """
        return self.create(feedback_set, request, *args, **kwargs)
