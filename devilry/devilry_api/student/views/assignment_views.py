# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.db.models import Q
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from devilry.apps.core.models.assignment_group import AssignmentGroup, Assignment
from devilry.devilry_api.auth.authentication import TokenAuthentication, SessionAuthentication
from devilry.devilry_api.student.serializers.assignment_serializers import (
    AssignmentGroupModelSerializer,
    AssignmentModelSerializer)


class AssignmentGroupListView(APIView):
    serializer_class = AssignmentGroupModelSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (TokenAuthentication, SessionAuthentication, )

    def get(self, request, *args, **kwargs):
        """
        list all assignment groups for user

        """
        assignment_groups = AssignmentGroup.objects.filter_user_is_candidate(self.request.user)
        serializer = self.serializer_class(assignment_groups, many=True)
        return Response(serializer.data)


class AssignmentListView(ListAPIView):
    """
    List view for assignments as an candidate

    Authentication is required.
    Authentication method allowed is by api key or session

    filters is passed as queryparams

    Examples:
        http://example.com/?subject=duck1010
        http://example.com/?ordering=publishing_time
        http://example.com/?semester=spring2015&ordering=-first_deadline

    """
    serializer_class = AssignmentModelSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (TokenAuthentication, SessionAuthentication, )
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['parentnode__parentnode__short_name', 'parentnode__short_name']

    def get_queryset(self):
        queryset_list = Assignment.objects.filter_user_is_candidate(self.request.user)
        semester = self.request.query_params.get('semester', None)
        subject = self.request.query_params.get('subject', None)
        if semester:
            queryset_list = queryset_list.filter(parentnode__short_name=semester).distinct()
        if subject:
            queryset_list = queryset_list.filter(parentnode__parentnode__short_name=subject).distinct()
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
            - name: semester
              required: false
              paramType: query
              type: String
              description: semester filter
            - name: subject
              required: false
              paramType: query
              type: String
              description: subject filter


        """
        return super(AssignmentListView, self).get(request, *args, **kwargs)
