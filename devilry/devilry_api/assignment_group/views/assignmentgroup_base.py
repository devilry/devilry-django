from django.db import models
from django.db.models.functions import Lower, Concat
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView

from devilry.apps.core.models.candidate import Candidate
from devilry.apps.core.models.examiner import Examiner
from devilry.devilry_api.auth.authentication import TokenAuthentication


class BaseAssignmentGroupView(ListAPIView):
    authentication_classes = (TokenAuthentication, )
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['parentnode__parentnode__parentnode__short_name',
                     'parentnode__parentnode__short_name',
                     'parentnode__short_name']

    @property
    def permission_classes(self):
        """
        Permission classes required

        Example:
            permission_classes = (IsAuthenticated, )

        Raises:
            :class:`NotImplementedError`
        """
        raise NotImplementedError("please set permission_classes example: permission_classes = (IsAuthenticated, )")

    @property
    def api_key_permissions(self):
        """
        Should be a list with API key permissions :class:`devilry_api.APIKey`.

        Example:
            api_key_permissions = (APIKey.STUDENT_PERMISSION_WRITE, APIKey.STUDENT_PERMISSION_READ)

        Raises:
            :class:`NotImplementedError`
        """
        raise NotImplementedError(
            "please set api_key_permission example: "
            "api_key_permissions = (APIKey.EXAMINER_PERMISSION_WRITE, APIKey.EXAMINER_PERMISSION_READ)")

    def get_role_query_set(self):
        """
        Returns queryset for role (examiner, student etc...).

        should return a :class:`~apps.core.AssignmentGroup` queryset.

        Raises:
            :class:`NotImplementedError`

        """
        raise NotImplementedError()

    def get_candidate_queryset(self):
        """
        Candidate queryset for prefetch

        Returns:
            :class:`~apps.core.Candidate` queryset
        """
        return Candidate.objects \
            .select_related('relatedstudent__user') \
            .order_by(
                Lower(Concat('relatedstudent__user__fullname',
                             'relatedstudent__user__shortname')))

    def get_examiner_queryset(self):
        """
        Examiner queryset for prefetch

        Returns:
            :class:`~apps.core.Examiner` queryset
        """
        return Examiner.objects \
            .select_related('relatedexaminer__user') \
            .order_by(
                Lower(Concat('relatedexaminer__user__fullname',
                             'relatedexaminer__user__shortname')))

    def get_queryset(self):
        """
        Checks query parameters and applies them if given.

        Returns:
            :class:`~apps.core.AssignmentGroup` queryset.

        """
        queryset = self.get_role_query_set() \
            .select_related('parentnode__parentnode__parentnode',
                            'cached_data__last_feedbackset',
                            'cached_data__first_feedbackset') \
            .prefetch_related(
                models.Prefetch('candidates',
                                queryset=self.get_candidate_queryset())) \
            .prefetch_related(
                models.Prefetch('examiners',
                                queryset=self.get_examiner_queryset())) \
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
        Get a list of assignment groups

        Search fields:
            :attr:`apps.core.Subject.short_name`
            :attr:`apps.core.Period.short_name`
            :attr:`apps.core.Assignment.short_name`

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
        return super(BaseAssignmentGroupView, self).get(request, *args, **kwargs)
