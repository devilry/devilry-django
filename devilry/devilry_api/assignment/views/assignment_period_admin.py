from rest_framework.generics import mixins

from devilry.apps.core.models import Assignment
from devilry.devilry_api.assignment.serializers.serializer_period_admin import PeriodAdminAssignmentSerializer
from devilry.devilry_api.assignment.views.assignment_base import BaseAssignmentView
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.period_admin_permission import PeriodAdminPermissionAPIKey


class PeriodAdminAssignmentView(mixins.CreateModelMixin,
                                BaseAssignmentView):
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
        return Assignment.objects.filter_user_is_period_admin(self.request.user)

    def get(self, request, *args, **kwargs):
        return super(PeriodAdminAssignmentView, self).get(request, *args, **kwargs)

    get.__doc__ = BaseAssignmentView.get.__doc__

    def post(self, request, *args, **kwargs):
        """
        Creates a new assignment with anonimization mode off.


        ---
        parameters:
            - name: period_id
              required: true
              paramType: form
              type: int
              description: id of period
            - name: long_name
              required: true
              paramType: form
              type: String
              description: long name of assignment
            - name: short_name
              paramType: form
              required: true
              type: String
              description: Up to 20 letters of lowercase english letters (a-z), numbers, underscore ("_") and hyphen
                ("-"). Used when the name takes too much space.
            - name: publishing_time
              paramType: form
              required: true
              type: DateTime
              description: The time when the assignment is to be published (visible to students and examiners).

        """
        return super(PeriodAdminAssignmentView, self).create(request, *args, **kwargs)
