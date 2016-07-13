# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from devilry.apps.core.models.assignment_group import AssignmentGroup
from devilry.devilry_api.auth.authentication import TokenAuthentication, SessionAuthentication
from devilry.devilry_api.student.serializers.assignment_serializers import AssignmentGroupModelSerializer


class AssignmentGroupListView(APIView):
    serializer_class = AssignmentGroupModelSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (TokenAuthentication, SessionAuthentication, )

    def get(self, request, *args, **kwargs):
        """
        list all assignments for user

        """
        assignment_groups = AssignmentGroup.objects.filter_user_is_candidate(self.request.user)
        serializer = self.serializer_class(assignment_groups, many=True)
        return Response(serializer.data)
