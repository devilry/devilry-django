# -*- coding: utf-8 -*-


from django.db import models

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.views import APIView

from devilry.apps.core import models as coremodels
from devilry.devilry_statistics.api.assignment.api_utils import AssignmentApiViewPreMixin, AccessPermission


class ExaminerAverageGradingPointsSerializer(serializers.Serializer):
    assignment_id = serializers.IntegerField(required=True)
    relatedexaminer_id = serializers.IntegerField(required=True)


class ExaminerAverageGradingPointsApi(AssignmentApiViewPreMixin, APIView):
    """
    API for getting the average score given by an examiner.
    """
    permission_classes = [IsAuthenticated, AccessPermission]

    def get_queryset(self, assignment, relatedexaminer):
        queryset = coremodels.AssignmentGroup.objects \
            .filter(parentnode_id=assignment.id) \
            .filter_user_is_examiner(user=relatedexaminer.user)
        return queryset

    def get_result(self, queryset):
        return queryset\
            .aggregate(average_grading_points=models.Avg('cached_data__last_published_feedbackset__grading_points'))\
            .get('average_grading_points') or 0

    def get_data(self, serializer):
        relatedexaminer = self.get_relatedexaminer(relatedexaminer_id=serializer.validated_data['relatedexaminer_id'])
        assignment = self.get_assignment(assignment_id=serializer.validated_data['assignment_id'])
        queryset = self.get_queryset(assignment=assignment, relatedexaminer=relatedexaminer)
        result = self.get_result(queryset=queryset)
        return {
            'average_grading_points_given': '{0:.2f}'.format(result),
            'user_name': relatedexaminer.user.get_full_name()
        }

    def get(self, *args, **kwargs):
        serializer = ExaminerAverageGradingPointsSerializer(data=kwargs)
        if serializer.is_valid():
            data = self.get_data(serializer=serializer)
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
