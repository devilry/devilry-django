from devilry.apps.core.models import Assignment
from devilry.devilry_api.assignment.serializers.serializer_period_admin import PeriodAdminAssignmentSerializer
from devilry.devilry_api.assignment.views.assignment_base import BaseAssignmentView
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.period_admin_permission import PeriodAdminPermissionAPIKey


class PeriodAdminAssignmentView(BaseAssignmentView):
    """
    Period admin view
    """
    serializer_class = PeriodAdminAssignmentSerializer
    api_key_permissions = (APIKey.ADMIN_PERMISSION_READ, APIKey.ADMIN_PERMISSION_WRITE)
    permission_classes = (PeriodAdminPermissionAPIKey, )

    def get_role_queryset(self):
        """
        Returns queryset for period admin role.
        Returns:
            :class:`~apps.core.Assignment` queryset
        """
        return Assignment.objects.filter_user_is_admin(self.request.user)

    def get(self, request, *args, **kwargs):
        return super(PeriodAdminAssignmentView, self).get(request, *args, **kwargs)

    get.__doc__ = BaseAssignmentView.get.__doc__
