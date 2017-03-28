from rest_framework.generics import mixins
from rest_framework.exceptions import PermissionDenied, ParseError
from django.utils.translation import ugettext_lazy

from devilry.apps.core.models import Assignment
from devilry.devilry_api.assignment.serializers.serializer_period_admin import PeriodAdminAssignmentSerializer
from devilry.devilry_api.assignment.views.assignment_base import BaseAssignmentView
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.period_admin_permission import PeriodAdminPermissionAPIKey


class PeriodAdminAssignmentView(mixins.CreateModelMixin,
                                mixins.UpdateModelMixin,
                                BaseAssignmentView):
    """
    Period admin view
    """
    serializer_class = PeriodAdminAssignmentSerializer
    api_key_permissions = (APIKey.ADMIN_PERMISSION_READ, APIKey.ADMIN_PERMISSION_WRITE)
    permission_classes = (PeriodAdminPermissionAPIKey, )

    def get_object(self):
        """
        Checks the required query parameter id, and returns the instance
        if instance exists return, otherwise raise Permission denied

        Returns:
            :obj:`devilry_group:Assignment`
        """
        id = self.request.query_params.get('id', None)
        if not id:
            raise ParseError(ugettext_lazy('query parameter "id" required'))

        instance = self.get_queryset().first()
        if not instance:
            raise PermissionDenied()
        return instance

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
            - name: first_deadline
              paramType: form
              required: true
              ty[e: DateTime
              description: The deadline date time of the first deadline.

        """
        return super(PeriodAdminAssignmentView, self).create(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Updates assignment with anonimization mode off.

        ---
        parameters:
            - name: id
              required: true
              paramType: query
              type: int
              description: id of assignment to update
        """
        return super(PeriodAdminAssignmentView, self).partial_update(request, *args, **kwargs)
