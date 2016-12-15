from rest_framework.generics import mixins

from devilry.apps.core.models.assignment_group import AssignmentGroup
from devilry.devilry_api.assignment_group.serializers.serializer_period_admin import AssignmentGroupModelSerializer
from devilry.devilry_api.assignment_group.views.assignmentgroup_base import BaseAssignmentGroupView
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.period_admin_permission import PeriodAdminPermissionAPIKey


class AssignmentGroupViewPeriodAdmin(mixins.CreateModelMixin,
                                     BaseAssignmentGroupView):
    permission_classes = (PeriodAdminPermissionAPIKey, )
    serializer_class = AssignmentGroupModelSerializer
    api_key_permissions = (APIKey.ADMIN_PERMISSION_READ, APIKey.ADMIN_PERMISSION_WRITE)

    def get_role_query_set(self):
        """
        Returns role queryset for period admin role

        Returns:
            :class:`~apps.core.AssignmentGroup` queryset
        """
        return AssignmentGroup.objects.filter_user_is_period_admin(self.request.user)

    def get(self, request, *args, **kwargs):
        return super(AssignmentGroupViewPeriodAdmin, self).get(request, *args, **kwargs)

    get.__doc__ = BaseAssignmentGroupView.get.__doc__

    def post(self, request, *args, **kwargs):
        """
        Creates a new assignment group for a assignment

        ---
        parameters:
            - name: assignment_id
              required: true
              paramType: form
              type: int
              description: id of assignment
            - name: name
              required: true
              paramType: form
              type: int
              description: name of assignment group

        """
        return super(AssignmentGroupViewPeriodAdmin, self).create(request, *args, **kwargs)
