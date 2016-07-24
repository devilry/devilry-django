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
    search_fields = ['parentnode__parentnode__short_name', 'parentnode__short_name']

    @property
    def permission_classes(self):
        raise NotImplementedError("please set permission_classes example: permission_classes = (IsAuthenticated, )")

    def get_role_queryset(self):
        raise NotImplementedError

    def get_queryset(self):
        queryset_list = self.get_role_queryset()
        semester = self.request.query_params.get('semester', None)
        subject = self.request.query_params.get('subject', None)
        if semester:
            queryset_list = queryset_list.filter(parentnode__short_name=semester).distinct()
        if subject:
            queryset_list = queryset_list.filter(parentnode__parentnode__short_name=subject).distinct()
        return queryset_list


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
