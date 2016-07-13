# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from rest_framework.response import Response
from rest_framework.views import APIView

from devilry.apps.core.models.assignment_group import AssignmentGroup
from devilry.devilry_api.assignment import serializers
from devilry.devilry_api.auth.authentication import TokenAuthentication


class AssignmentView(APIView):
    serializer_class = serializers.AssignmentModelSerializer
    authentication_classes = (TokenAuthentication, )

    def get(self, request, *args, **kwargs):
        """
        list all assignments for user


        """
        assignment_groups = AssignmentGroup.objects.filter_user_is_candidate(self.request.user)
        serializer = self.serializer_class(assignment_groups, many=True)
        return Response(serializer.data)
