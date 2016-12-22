from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.feedbackset.serializers.serializer_period_admin import FeedbacksetSerializerPeriodAadmin
from devilry.devilry_api.feedbackset.views.feedbackset_base import BaseFeedbacksetView
from devilry.devilry_api.permission.period_admin_permission import PeriodAdminPermissionAPIKey


class FeedbacksetViewPeriodAdmin(BaseFeedbacksetView):
    permission_classes = (PeriodAdminPermissionAPIKey, )
    api_key_permissions = (APIKey.ADMIN_PERMISSION_READ, APIKey.ADMIN_PERMISSION_WRITE)
    serializer_class = FeedbacksetSerializerPeriodAadmin

    def get_role_query_set(self):
        """
        Returns role queryset for period admin role

        Returns:
            :class:`~devilry_group.Feedbackset` queryset
        """
        assignment_group_queryset = AssignmentGroup.objects.filter_user_is_period_admin(user=self.request.user)
        return FeedbackSet.objects.filter(group=assignment_group_queryset)

    def get(self, request, *args, **kwargs):
        return super(FeedbacksetViewPeriodAdmin, self).get(request, *args, **kwargs)

    get.__doc__ = BaseFeedbacksetView.get.__doc__
