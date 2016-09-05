# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from devilry.apps.core.models.assignment_group import Assignment
from devilry.devilry_api.assignment.serializers.serializer_examiner import ExaminerAssignmentSerializer
from devilry.devilry_api.assignment.views.assignment_base import AssignmentListViewBase
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.examiner_permission import ExaminerPermissionAPIKey


class AssignmentListView(AssignmentListViewBase):
    """
    List view for assignments as Examiner
    """
    serializer_class = ExaminerAssignmentSerializer
    permission_classes = (ExaminerPermissionAPIKey, )
    api_key_permissions = (APIKey.EXAMINER_PERMISSION_READ, APIKey.EXAMINER_PERMISSION_WRITE)

    def get_role_queryset(self):
        """
        Returns queryset for examiner role.

        Returns:
            :class:`~apps.core.Assignment` queryset
        """
        return Assignment.objects.filter_examiner_has_access(self.request.user)

    def get(self, request, *args, **kwargs):
        return super(AssignmentListView, self).get(request, *args, **kwargs)

    get.__doc__ = AssignmentListViewBase.get.__doc__
