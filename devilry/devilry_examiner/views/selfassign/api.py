from django.core.exceptions import PermissionDenied
from django.http import Http404
import time

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from devilry.apps.core.models import AssignmentGroup, Examiner
from devilry.devilry_examiner.views.selfassign import utils as selfassign_utils


class ExaminerSelfAssignApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        raise Http404()

    def examiner_can_assign(self):
        requestuser = self.request.user
        return True

    def examiner_can_unassign(self):
        group_is_available_to_user = selfassign_utils.assignment_groups_available_for_self_assign(
            period=self.assignment_group.parentnode.parentnode.id,
            user=self.request.user
        ).exists()
        user_is_examiner_for_group = Examiner.objects \
            .filter(
                assignmentgroup=self.assignment_group,
                relatedstudent__user=self.request.user) \
            .exists()
        print(group_is_available_to_user)
        print(user_is_examiner_for_group)
        return group_is_available_to_user and user_is_examiner_for_group

    def assign_to_group(self):
        pass

    def unassign_from_group(self):
        examiner_instance = Examiner.objects \
            .filter(
                assignmentgroup=self.assignment_group,
                relatedexaminer__user=self.request.user
            ).get()
        examiner_instance.delete()

    def post(self, request, *args, **kwargs):
        time.sleep(2)
        self.assignment_group = AssignmentGroup.objects \
            .get(id=self.kwargs['group_id'])

        action = request.data.get('action')
        print(action)
        if action == 'ASSIGN' and self.examiner_can_assign():
            self.assign_to_group()
        elif action == 'UNASSIGN' and self.examiner_can_unassign():
            self.unassign_from_group()

        return Response({'status': 'assigned'}, status=status.HTTP_200_OK)
        # return Response({'status': 'assigned'}, status=status.HTTP_400_BAD_REQUEST)
