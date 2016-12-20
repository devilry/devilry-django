from rest_framework.generics import mixins


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
        return GroupComment.objects.filter(feedback_set__group=assignment_group_queryset,
                                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT) \
            .exclude_private_comments_from_other_users(user=self.request.user)

    def get(self, request, feedback_set, *args, **kwargs):
        return super(GroupCommentViewPeriodAdmin, self).get(request, feedback_set, *args, **kwargs)

    get.__doc__ = BaseGroupCommentView.get.__doc__
