# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from devilry.apps.core.models.assignment_group import Assignment
from devilry.devilry_api.assignment.serializers.serializer_student import StudentAssignmentSerializer
from devilry.devilry_api.assignment.views.assignment_base import BaseAssignmentView
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.student_permission import StudentPermissionAPIKey


class AssignmentListView(BaseAssignmentView):
    """
    List view for assignments as an candidate

    """
    serializer_class = StudentAssignmentSerializer
    permission_classes = (StudentPermissionAPIKey, )

    #: api key permissions allowed
    api_key_permissions = (APIKey.STUDENT_PERMISSION_READ, APIKey.STUDENT_PERMISSION_WRITE)

    def get_role_queryset(self):
        """
        Returns queryset for student role.

        Returns:
            :class:`~apps.core.Assignment` queryset
        """
        return Assignment.objects.filter_student_has_access(self.request.user)

    def get(self, request, *args, **kwargs):
        return super(AssignmentListView, self).get(request, *args, **kwargs)

    get.__doc__ = BaseAssignmentView.get.__doc__
