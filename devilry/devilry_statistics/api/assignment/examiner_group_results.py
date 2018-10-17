# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.views import APIView

from devilry.apps.core import models as coremodels
from devilry.devilry_statistics.api.assignment.api_utils import AssignmentApiViewPreMixin, AccessPermission


class ExaminerGroupResultsSerializer(serializers.Serializer):
    assignment_id = serializers.IntegerField(required=True)
    relatedexaminer_id = serializers.IntegerField(required=True)


class ExaminerGroupResultApi(AssignmentApiViewPreMixin, APIView):
    """
    API for getting the percentage of groups passed, failed and not corrected for an examiner.
    """
    permission_classes = [IsAuthenticated, AccessPermission]

    def get_queryset(self, assignment, relatedexaminer):
        queryset = coremodels.AssignmentGroup.objects \
            .filter(parentnode_id=assignment.id) \
            .filter_user_is_examiner(user=relatedexaminer.user)
        return queryset

    def get_result(self, queryset):
        return queryset\
            .aggregate(
                total_group_count=models.Count('id'),
                num_groups_passed=models.Count(models.Case(
                    models.When(
                        cached_data__last_published_feedbackset__isnull=False,
                        cached_data__last_feedbackset=models.F('cached_data__last_published_feedbackset'),
                        cached_data__last_published_feedbackset__grading_points__gte=models.F(
                            'parentnode__passing_grade_min_points'),
                        then=1)
                )),
                num_groups_failed=models.Count(models.Case(
                    models.When(
                        cached_data__last_published_feedbackset__isnull=False,
                        cached_data__last_feedbackset=models.F('cached_data__last_published_feedbackset'),
                        cached_data__last_published_feedbackset__grading_points__lt=models.F(
                            'parentnode__passing_grade_min_points'),
                        then=1)
                )),
                num_groups_not_corrected=models.Count(models.Case(
                    models.When(
                        models.Q(cached_data__last_feedbackset__grading_published_datetime__isnull=True),
                        then=1)
                )))

    def get_percentage(self, p, total):
        if p == 0 or total == 0:
            return 0
        return 100 * (float(p) / float(total))

    def get_data(self, serializer):
        relatedexaminer = self.get_relatedexaminer(relatedexaminer_id=serializer.validated_data['relatedexaminer_id'])
        assignment = self.get_assignment(assignment_id=serializer.validated_data['assignment_id'])
        queryset = self.get_queryset(assignment=assignment, relatedexaminer=relatedexaminer)
        result = self.get_result(queryset=queryset)
        total_group_count = result.get('total_group_count')
        groups_passed = result.get('num_groups_passed')
        groups_failed = result.get('num_groups_failed')
        groups_not_corrected = result.get('num_groups_not_corrected')
        data = {
            'groups_passed': '{0:.2f}'.format(self.get_percentage(p=groups_passed, total=total_group_count)),
            'groups_failed': '{0:.2f}'.format(self.get_percentage(p=groups_failed, total=total_group_count)),
            'groups_not_corrected': '{0:.2f}'.format(self.get_percentage(p=groups_not_corrected, total=total_group_count)),
            'user_name': relatedexaminer.user.get_full_name()
        }
        return data

    def get(self, *args, **kwargs):
        serializer = ExaminerGroupResultsSerializer(data=kwargs)
        if serializer.is_valid():
            data = self.get_data(serializer=serializer)
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)