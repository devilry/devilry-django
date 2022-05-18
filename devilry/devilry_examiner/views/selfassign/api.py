from django.core.exceptions import PermissionDenied
from django.http import Http404
import time

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from devilry.apps.core.models import AssignmentGroup, Examiner, RelatedExaminer, Period
from devilry.devilry_examiner.views.selfassign import utils as selfassign_utils


class ExaminerSelfAssignApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        raise Http404()

    def is_assigned_to_group(self):
        return Examiner.objects \
            .filter(
                assignmentgroup=self.assignment_group,
                relatedexaminer__user=self.request.user) \
            .exists()

    def assign_to_group(self):
        if not self.is_assigned_to_group():
            relatedexaminer = RelatedExaminer.objects \
                .filter(active=True) \
                .get(period=self.period, user=self.request.user)
            examiner = Examiner(assignmentgroup=self.assignment_group, relatedexaminer=relatedexaminer)
            examiner.full_clean()
            examiner.save()

    def unassign_from_group(self):
        if self.is_assigned_to_group():
            examiner = Examiner.objects \
                .filter(
                    assignmentgroup=self.assignment_group,
                    relatedexaminer__user=self.request.user
                ) \
                .get()
            examiner.delete()

    def post(self, request, *args, **kwargs):
        try:
            self.period = Period.objects \
                .filter_active() \
                .get(id=self.kwargs['period_id'])
        except Period.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate and get AssignmentGroup
        group_id = request.data.get('group_id', None)
        if group_id is None:
            return Response(
                {'error': 'Missing "group_id".'},
                status=status.HTTP_400_BAD_REQUEST  
            )
        try:
            self.assignment_group = selfassign_utils \
                .assignment_groups_available_for_self_assign(
                    period=self.period,
                    user=self.request.user
                ) \
                .get(id=group_id)
        except AssignmentGroup.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate action
        action = request.data.get('action', None)
        if action is None:
            return Response(
              {'error': 'Missing "action".'},
              status=status.HTTP_400_BAD_REQUEST
            )
        if action not in ['ASSIGN', 'UNASSIGN']:
            return Response(
                {'error': f'Unknown action "{action}".'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Perform assign/unassign
        if action == 'ASSIGN':
            self.assign_to_group()
            return Response({'status': 'assigned'}, status=status.HTTP_200_OK)
        elif action == 'UNASSIGN':
            self.unassign_from_group()
            return Response({'status': 'unassigned'}, status=status.HTTP_200_OK)
        return Response({'error': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)
