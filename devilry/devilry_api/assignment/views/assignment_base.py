# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView

from devilry.devilry_api.assignment.serializers import (
    AssignmentModelSerializer)
from devilry.devilry_api.auth.authentication import TokenAuthentication


class AssignmentListViewBase(ListAPIView):
    serializer_class = AssignmentModelSerializer
    authentication_classes = (TokenAuthentication, )
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['parentnode__parentnode__short_name', 'parentnode__short_name', 'short_name']

    @property
    def permission_classes(self):
        raise NotImplementedError("please set permission_classes example: permission_classes = (IsAuthenticated, )")

    @property
    def api_key_permissions(self):
        """
        Should be a list with API key permissions :class:`devilry_api.APIKey`.

        Example:
            api_key_permissions = (APIKey.STUDENT_PERMISSION_WRITE, APIKey.STUDENT_PERMISSION_READ)

        Returns:
            list with api keys
        """
        raise NotImplementedError(
            "please set api_key_permission example: "
            "api_key_permissions = (APIKey.EXAMINER_PERMISSION_WRITE, APIKey.EXAMINER_PERMISSION_READ)")

    def get_role_queryset(self):
        """
        Returns queryset for role (examiner, student etc...).

        Returns:
            :class:`~apps.core.Assignment` queryset.

        """
        raise NotImplementedError()

    def get_queryset(self):
        """
        Checks query parameters and applies them if given.

        Returns:
            :class:`~apps.core.Assignment` queryset.

        """
        queryset_list = self.get_role_queryset().select_related('parentnode__parentnode')
        period_short_name = self.request.query_params.get('period_short_name', None)
        subject_short_name = self.request.query_params.get('subject_short_name', None)
        short_name = self.request.query_params.get('short_name', None)
        id = self.request.query_params.get('id', None)
        if id:
            queryset_list = queryset_list.filter(id=id).distinct()
        if period_short_name:
            queryset_list = queryset_list.filter(parentnode__short_name=period_short_name).distinct()
        if subject_short_name:
            queryset_list = queryset_list.filter(parentnode__parentnode__short_name=subject_short_name).distinct()
        if short_name:
            queryset_list = queryset_list.filter(short_name=short_name).distinct()
        return queryset_list

    def get(self, request, *args, **kwargs):
        """
        Get a list of assignments.

        Search fields:
            :attr:`apps.core.Subject.short_name`
            :attr:`apps.core.Period.short_name`
            :attr:`apps.core.Assignment.short_name`

        Examples:
            /?subject=duck1010
            /?ordering=publishing_time
            /?semester=spring2015&ordering=-first_deadline
            /?search=duck1010
        ---
        parameters:
            - name: ordering
              required: false
              paramType: query
              type: String
              description: ordering field
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
            - name: short_name
              required: false
              paramType: query
              type: String
              description: assignment short_name filter
            - name: id
              required: false
              paramType: query
              type: Int
              description: assignment id filter

        """
        return super(AssignmentListViewBase, self).get(request, *args, **kwargs)
