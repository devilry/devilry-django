from django import forms
from django.db import transaction
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.views import View
from djangorestframework.resources import FormResource
from djangorestframework.response import ErrorResponse
from djangorestframework import status

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models.assignment_group import GroupPopValueError
from devilry.apps.core.models import Candidate
from .auth import IsAssignmentAdmin
from .errors import NotFoundError


class PopFromGroupForm(forms.Form):
    group_id = forms.IntegerField(required=True)
    candidate_id = forms.IntegerField(required=True,
                                      help_text='The ID of the candidate to pop.')

class PopFromGroupResource(FormResource):
    form = PopFromGroupForm


class PopFromGroup(View):
    permissions = (IsAuthenticated, IsAssignmentAdmin)
    resource = PopFromGroupResource

    def _get_group(self, group_id):
        try:
            return AssignmentGroup.objects.get(parentnode=self.assignment_id,
                                         id=group_id)
        except AssignmentGroup.DoesNotExist:
            raise NotFoundError(('Group with assignment_id={assignment_id} and '
                                 'id={group_id} not found').format(assignment_id=self.assignment_id,
                                                                   group_id=group_id))

    def _get_candidate(self, group_id, candidate_id):
        try:
            return Candidate.objects.get(assignment_group=group_id,
                                         id=candidate_id)
        except Candidate.DoesNotExist:
            raise NotFoundError(('Candidate with candidate_id={candidate_id} and '
                                 'group_id={group_id} not found').format(group_id=group_id,
                                                                         candidate_id=candidate_id))

    def post(self, request, id):
        self.assignment_id = id
        group_id = self.CONTENT['group_id']
        candidate_id = self.CONTENT['candidate_id']
        group = self._get_group(group_id)
        candidate = self._get_candidate(group_id, candidate_id)
        with transaction.commit_on_success():
            try:
                new_group = group.pop_candidate(candidate)
            except GroupPopValueError as e:
                raise ErrorResponse(status.HTTP_400_BAD_REQUEST, {'detail': str(e)})
        return {'success': True,
                'group_id': group_id,
                'new_group_id': new_group.id,
                'candidate_id': candidate_id}
