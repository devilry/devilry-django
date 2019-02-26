# -*- coding: utf-8 -*-


from django.db import models
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.views import APIView

from devilry.apps.core import models as coremodels
from devilry.devilry_statistics.api.assignment.api_utils import AssignmentApiViewPreMixin, AccessPermission


class ExaminerDetailsSerializer(serializers.Serializer):
    assignment_id = serializers.IntegerField(required=True)
    relatedexaminer_id = serializers.IntegerField(required=True)


class ExaminerDetailsApi(AssignmentApiViewPreMixin, APIView):
    """
    API for getting details about each examiner, corrected groups total, passed, failed, groups waiting for feedback
    and so on.
    """
    permission_classes = [IsAuthenticated, AccessPermission]

    def get_queryset(self, assignment, relatedexaminer):
        queryset = coremodels.AssignmentGroup.objects \
            .filter(parentnode_id=assignment.id) \
            .filter_user_is_examiner(user=relatedexaminer.user)
        return queryset

    def get_result(self, queryset):
        now = timezone.now()
        return queryset \
            .aggregate(
                total_group_count=models.Count('id'),
                groups_with_passing_grade_count=models.Count(models.Case(
                    models.When(
                        cached_data__last_published_feedbackset__isnull=False,
                        cached_data__last_feedbackset=models.F('cached_data__last_published_feedbackset'),
                        cached_data__last_published_feedbackset__grading_points__gte=models.F(
                            'cached_data__group__parentnode__passing_grade_min_points'),
                        then=1)
                )),
                groups_corrected_count=models.Count(models.Case(
                    models.When(
                        cached_data__last_feedbackset=models.F('cached_data__last_published_feedbackset'),
                        then=1)
                )),
                groups_with_failing_grade_count=models.Count(models.Case(
                    models.When(
                        cached_data__last_published_feedbackset__isnull=False,
                        cached_data__last_feedbackset=models.F('cached_data__last_published_feedbackset'),
                        cached_data__last_published_feedbackset__grading_points__lt=models.F(
                            'parentnode__passing_grade_min_points'),
                        then=1)
                )),
                groups_waiting_for_deliveries_count=models.Count(models.Case(
                    models.When(
                        cached_data__last_feedbackset__grading_published_datetime__isnull=True,
                        cached_data__last_feedbackset__deadline_datetime__gt=now,
                        then=1
                    )
                )),
                groups_waiting_for_feedback_count=models.Count(models.Case(
                    models.When(
                        cached_data__last_feedbackset__grading_published_datetime__isnull=True,
                        cached_data__last_feedbackset__deadline_datetime__lt=now,
                        then=1)
                )),
                groups_waiting_for_deadline_to_expire_count=models.Count(models.Case(
                    models.When(
                        cached_data__last_feedbackset__grading_published_datetime__isnull=True,
                        cached_data__last_feedbackset__deadline_datetime__gt=now,
                        then=1)
                )),
                points_average=models.Avg('cached_data__last_published_feedbackset__grading_points'),
                points_highest=models.Max('cached_data__last_published_feedbackset__grading_points'),
                points_lowest=models.Min('cached_data__last_published_feedbackset__grading_points')
            )

    def get_data(self, serializer):
        relatedexaminer = self.get_relatedexaminer(relatedexaminer_id=serializer.validated_data['relatedexaminer_id'])
        assignment = self.get_assignment(assignment_id=serializer.validated_data['assignment_id'])
        queryset = self.get_queryset(assignment=assignment, relatedexaminer=relatedexaminer)
        result = self.get_result(queryset=queryset)
        return {
            'total_group_count': result.get('total_group_count'),
            'groups_corrected_count': result.get('groups_corrected_count'),
            'groups_with_passing_grade_count': result.get('groups_with_passing_grade_count'),
            'groups_with_failing_grade_count': result.get('groups_with_failing_grade_count'),
            'groups_waiting_for_deliveries_count': result.get('groups_waiting_for_deliveries_count'),
            'groups_waiting_for_feedback_count': result.get('groups_waiting_for_feedback_count'),
            'groups_waiting_for_deadline_to_expire_count': result.get('groups_waiting_for_deadline_to_expire_count'),
            'points_average': '{0:.2f}'.format(result.get('points_average') or 0),
            'points_highest': '{0:.2f}'.format(result.get('points_highest') or 0),
            'points_lowest': '{0:.2f}'.format(result.get('points_lowest') or 0),
            'user_name': relatedexaminer.user.get_full_name()
        }

    def get(self, *args, **kwargs):
        serializer = ExaminerDetailsSerializer(data=kwargs)
        if serializer.is_valid():
            data = self.get_data(serializer=serializer)
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
