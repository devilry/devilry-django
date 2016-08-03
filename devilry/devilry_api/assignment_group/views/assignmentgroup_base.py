from django.db import models
from django.db.models.functions import Lower, Concat
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView

from devilry.apps.core.models.candidate import Candidate
from devilry.apps.core.models.examiner import Examiner
from devilry.devilry_api.auth.authentication import TokenAuthentication


class AssignmentGroupListViewBase(ListAPIView):
    authentication_classes = (TokenAuthentication, )
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['parentnode__parentnode__parentnode__short_name',
                     'parentnode__parentnode__short_name',
                     'parentnode__short_name']

    @property
    def permission_classes(self):
        raise NotImplementedError("please set permission_classes example: permission_classes = (IsAuthenticated, )")

    def get_role_query_set(self):
        raise NotImplementedError()

    def get_candidate_queryset(self):
        return Candidate.objects \
            .select_related('relatedstudent__user') \
            .order_by(
                Lower(Concat('relatedstudent__user__fullname',
                             'relatedstudent__user__shortname')))

    def get_examiner_queryset(self):
        return Examiner.objects \
            .select_related('relatedexaminer__user') \
            .order_by(
                Lower(Concat('relatedexaminer__user__fullname',
                             'relatedexaminer__user__shortname')))

    def get_queryset(self):
        queryset = self.get_role_query_set() \
            .select_related('parentnode__parentnode__parentnode') \
            .prefetch_related(
                models.Prefetch('candidates',
                                queryset=self.get_candidate_queryset())) \
            .prefetch_related(
                models.Prefetch('examiners',
                                queryset=self.get_examiner_queryset())) \
            .annotate_with_grading_points() \
            .annotate_with_is_waiting_for_feedback() \
            .annotate_with_is_waiting_for_deliveries() \
            .annotate_with_is_corrected() \
            .distinct()

        id = self.request.query_params.get('id', None)
        assignment_id = self.request.query_params.get('assignment_id', None)
        period_short_name = self.request.query_params.get('period_short_name', None)
        subject_short_name = self.request.query_params.get('subject_short_name', None)
        assignment_short_name = self.request.query_params.get('assignment_short_name', None)
        if id:
            queryset = queryset.filter(id=id).distinct()
        if assignment_id:
            queryset = queryset.filter(parentnode__id=assignment_id).distinct()
        if period_short_name:
            queryset = queryset.filter(parentnode__parentnode__short_name=period_short_name).distinct()
        if subject_short_name:
            queryset = queryset.filter(parentnode__parentnode__parentnode__short_name=subject_short_name).distinct()
        if assignment_short_name:
            queryset = queryset.filter(parentnode__short_name=assignment_short_name).distinct()

        return queryset

    def get(self, request, *args, **kwargs):
        """
        Gets a list of assignment groups

        ---
        parameters:
            - name: ordering
              required: false
              paramType: query
              type: String
              description: ordering
            - name: search
              required: false
              paramType: query
              type: String
              description: search fields(subject, period)
            - name: period_short_name
              required: false
              paramType: query
              type: String
              description: period filter
            - name: subject_short_name
              required: false
              paramType: query
              type: String
              description: subject filter
            - name: assignment_short_name
              required: false
              paramType: query
              type: String
              description: assignment filter
            - name: id
              required: false
              paramType: query
              type: Int
              description: assignment group id filter
            - name: assignment_id
              required: false
              paramType: query
              type: Int
              description: assignment id filter


        """
        return super(AssignmentGroupListViewBase, self).get(request, *args, **kwargs)
