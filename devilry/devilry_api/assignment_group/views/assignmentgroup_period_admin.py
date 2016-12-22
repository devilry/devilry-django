from django.utils.translation import ugettext_lazy
from rest_framework.generics import mixins
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import status

from devilry.apps.core.models.assignment_group import AssignmentGroup
from devilry.devilry_api.assignment_group.serializers.serializer_period_admin import AssignmentGroupModelSerializer
from devilry.devilry_api.assignment_group.views.assignmentgroup_base import BaseAssignmentGroupView
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.period_admin_permission import PeriodAdminPermissionAPIKey


class AssignmentGroupViewPeriodAdmin(mixins.CreateModelMixin,
                                     mixins.DestroyModelMixin,
                                     BaseAssignmentGroupView):
    permission_classes = (PeriodAdminPermissionAPIKey, )
    serializer_class = AssignmentGroupModelSerializer
    api_key_permissions = (APIKey.ADMIN_PERMISSION_READ, APIKey.ADMIN_PERMISSION_WRITE)

    def get_object(self):
        """
        gets an :obj:`devilry_group.AssignmentGroup`

        Returns:
            :obj:`~apps.core.AssignmentGroup`

        Raises:
            :class:`rest_framework.exceptions.NotFound`
        """
        id = self.request.query_params.get('id', None)
        if not id:
            raise exceptions.ParseError(ugettext_lazy('query parameter "id" required.'))

        instance = self.get_queryset().first()
        if not instance:
            raise exceptions.NotFound(ugettext_lazy('Assignment group with id: {} not found.'.format(id)))
        return instance

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

    # def post(self, request, *args, **kwargs):
    #     """
    #     Creates a new assignment group for a assignment
    #
    #     ---
    #     parameters:
    #         - name: assignment_id
    #           required: true
    #           paramType: form
    #           type: int
    #           description: id of assignment
    #         - name: name
    #           required: true
    #           paramType: form
    #           type: int
    #           description: name of assignment group
    #
    #     """
    #     return super(AssignmentGroupViewPeriodAdmin, self).create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Destroys an Assignment group if there is no students at the assignment group

        ---
        parameters:
            - name: id
              required: true
              paramType: query
              type: Int
              description: id of assignment group to remove

        """
        instance = self.get_object()
        if instance.candidates.count() is 0:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise exceptions.PermissionDenied(ugettext_lazy('Permission denied: cannot delete assignment group.'))
