# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission

from devilry.apps.core import models as coremodels
from devilry.devilry_account.models import PeriodPermissionGroup


class AssignmentApiViewPreMixin(object):
    def get_relatedexaminer(self, relatedexaminer_id):
        try:
            return coremodels.RelatedExaminer.objects.get(id=relatedexaminer_id)
        except coremodels.RelatedExaminer.DoesNotExist:
            raise NotFound({'error': 'Examiner does not exist.'})

    def get_assignment(self, assignment_id):
        try:
            return coremodels.Assignment.objects.get(id=assignment_id)
        except coremodels.Assignment.DoesNotExist:
            raise NotFound({'error': 'Assignment does not exist.'})

    def get_queryset(self, assignment, relatedexaminer):
        raise NotImplementedError()

    def get_data(self, serializer):
        raise NotImplementedError()


class AccessPermission(BasePermission):
    def has_permission(self, request, view):
        assignment_id = view.kwargs.get('assignment_id')
        try:
            assignment = coremodels.Assignment.objects.get(id=assignment_id)
        except coremodels.Assignment.DoesNotExist:
            return False
        devilryrole = PeriodPermissionGroup.objects.get_devilryrole_for_user_on_period(
            user=request.user,
            period=assignment.period
        )
        if devilryrole is None:
            return False
        return True
