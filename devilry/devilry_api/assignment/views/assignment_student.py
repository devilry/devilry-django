# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from devilry.devilry_api.permission.student_permission import StudentReadOnlyAPIKey
from devilry.apps.core.models.assignment_group import Assignment
from devilry.devilry_api.assignment.views.assignment_base import AssignmentListViewBase, AssignmentViewBase


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
    permission_classes = (StudentReadOnlyAPIKey, )

    def get_role_queryset(self):
        return Assignment.objects.filter_student_has_access(self.request.user) \
            .select_related('parentnode__parentnode')

    def get(self, request, *args, **kwargs):
        return super(AssignmentListView, self).get(request, *args, **kwargs)

    get.__doc__ = AssignmentListViewBase.get.__doc__


class AssignmentView(AssignmentViewBase):
    """
    student assignment view
    get a specific assignment by subject, semester and assignment name

    Authentication is required.
    Authentication method allowed is by api key or session

    Examples:
        /inf1000/v15/assignment1
    """
    permission_classes = (StudentReadOnlyAPIKey, )

    def get_role_queryset(self):
        return Assignment.objects.filter_student_has_access(self.request.user)

    def get(self, request, subject, semester, assignment, *args, **kwargs):
        """
        Get a specific assignment

        ---
        parameters:
            - name: subject
              required: true
              paramType: path
              type: String
              description: subject(INF1000)
            - name: semester
              required: true
              paramType: path
              type: String
              description: semester(V15)
            - name: assignment
              required: true
              paramType: path
              type: String
              description: assignment(assignment1)

        """
        return super(AssignmentView, self).get(request, subject, semester, assignment, *args, **kwargs)
