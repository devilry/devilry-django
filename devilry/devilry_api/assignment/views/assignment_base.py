# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.http import Http404
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response

from devilry.apps.core.models.assignment_group import Assignment
from devilry.devilry_api.assignment.serializers import (
    AssignmentModelSerializer)
from devilry.devilry_api.auth.authentication import TokenAuthentication, SessionAuthentication


class AssignmentListViewBase(ListAPIView):
    """
    Base assignment list view

    Authentication is required.
    Authentication method allowed is by api key or session

    filters is passed as queryparams

    Examples:
        /?subject=duck1010
        /?ordering=publishing_time
        /?semester=spring2015&ordering=-first_deadline

    """
    serializer_class = AssignmentModelSerializer
    authentication_classes = (TokenAuthentication, )
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['parentnode__parentnode__short_name', 'parentnode__short_name', 'short_name']

    @property
    def permission_classes(self):
        raise NotImplementedError("please set permission_classes example: permission_classes = (IsAuthenticated, )")

    def get_role_queryset(self):
        raise NotImplementedError()

    def get_queryset(self):
        queryset_list = self.get_role_queryset()
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
        Gets a list of assignments

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
              description: search fields(subject, semester)
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


class AssignmentViewBase(GenericAPIView):
    """
    Base assignment view

    Authentication is required.
    Authentication method allowed is by api key or session

    Examples:
        /inf1000/v15/assignment1
    """
    serializer_class = AssignmentModelSerializer
    authentication_classes = (TokenAuthentication, )

    @property
    def permission_classes(self):
        raise NotImplementedError("please set permission_classes example: permission_classes = (IsAuthenticated, )")

    def get_role_queryset(self):
        raise NotImplementedError

    def get_queryset(self):
        return self.get_role_queryset()

    def get(self, request, subject, semester, assignment, *args, **kwargs):
        try:
            queryset = self.get_queryset().get(parentnode__parentnode__short_name=subject,
                                               parentnode__short_name=semester,
                                               short_name=assignment)
        except Assignment.DoesNotExist:
            raise Http404
        serializer = self.serializer_class(queryset)
        return Response(serializer.data)