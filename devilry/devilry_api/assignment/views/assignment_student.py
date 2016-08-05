# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from devilry.apps.core.models.assignment_group import Assignment
from devilry.devilry_api.assignment.views.assignment_base import AssignmentListViewBase
from devilry.devilry_api.models import APIKey
from devilry.devilry_api.permission.student_permission import StudentPermissionAPIKey


class AssignmentListView(AssignmentListViewBase):
    """
    List view for assignments as an candidate

    Authentication is required.
    Authentication method allowed is by api key or session

    filters is passed as queryparams

    Examples:
        /?subject=duck1010
        /?ordering=publishing_time
        /?semester=spring2015&ordering=-first_deadline

    """
    permission_classes = (StudentPermissionAPIKey, )

    #: api key permissions allowed
    api_key_permissions = (APIKey.STUDENT_PERMISSION_READ, APIKey.STUDENT_PERMISSION_WRITE)

    def get_role_queryset(self):
        return Assignment.objects.filter_student_has_access(self.request.user)

    def get(self, request, *args, **kwargs):
        return super(AssignmentListView, self).get(request, *args, **kwargs)

    get.__doc__ = AssignmentListViewBase.get.__doc__
