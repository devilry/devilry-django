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
from devilry.devilry_subjectadmin.rest.auth import IsAssignmentAdmin
from .errors import NotFoundError
from .log import logger


class PopFromGroupForm(forms.Form):
    group_id = forms.IntegerField(required=True)
    candidate_id = forms.IntegerField(required=True,
                                      help_text='The ID of the candidate to pop.')

class PopFromGroupResource(FormResource):
    form = PopFromGroupForm


class PopFromGroup(View):
    """
    REST API for the ``pop_candidate`` method of ``devilry.apps.code.models.AssignmentGroup``.

    # POST
    Pop a candidate from a group(called source), copy the source, except for
    the candidates, and add the popped candidate to the newly created group.

    ## Parameters
    The assignment ID is the last part of the URL.
    The following parameters must be part of the request body:

    - ``group_id`` (int): The ID of the source group.
    - ``candidate_id`` (int): The ID of the candidate. Must be a candidate in the source group.

    ## Response
    Responds with status code ``200`` and an object/map with the following attributes on success:

    - ``success`` (bool): Always ``true``.
    - ``group_id`` (int): The ID of the source group.
    - ``candidate_id`` (int): The ID of the candidate.
    - ``new_group_id`` (int): The ID of the newly created group.

    On error, we respond with:

    - Errorcode ``400`` if any of the parameters are missing or wrong.
    - Errorcode ``403`` for permission denied.
    - Errorcode ``404`` if the group is not found within the assignment, or if the candidate is not found within the group.
    """
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
        logger.info('User %s moving candidate %r from %r into a copy of the group.',
                    request.user.username, candidate, group)
        with transaction.commit_on_success():
            try:
                new_group = group.pop_candidate(candidate)
            except GroupPopValueError as e:
                raise ErrorResponse(status.HTTP_400_BAD_REQUEST, {'detail': str(e)})
        logger.info('User %s successfully moved candidate %r from %r into %r.',
                    request.user.username, candidate, group, new_group)
        return {'success': True,
                'group_id': group_id,
                'new_group_id': new_group.id,
                'candidate_id': candidate_id}
