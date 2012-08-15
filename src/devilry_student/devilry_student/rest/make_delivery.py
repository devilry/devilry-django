from djangorestframework.permissions import BasePermission
from djangorestframework.response import ErrorResponse
from djangorestframework import status

from devilry.apps.core.models import AssignmentGroup
from .aggregated_groupinfo import GroupResource
from .aggregated_groupinfo import AggregatedGroupInfo



class IsCandidate(BasePermission):
    """
    Djangorestframework permission checker that checks if the requesting user
    is candidate on the requested group.
    """
    def check_permission(self, user):
        groupid = self.view.kwargs['id']
        try:
            AssignmentGroup.where_is_candidate(user).get(id=groupid)
        except AssignmentGroup.DoesNotExist, e:
            raise ErrorResponse(status.HTTP_403_FORBIDDEN,
                                {'detail': 'Only candidates on group with ID={0} can make this request.'.format(groupid)})


class MinimalGroupResource(GroupResource):
    fields = ('id', 'name', 'is_open', 'candidates', 'active_feedback',
              'deadline_handling', 'breadcrumbs')


class MakeDeliveryGroupInfo(AggregatedGroupInfo):
    """
    Provides an API that gives us the information that we need about a group to
    make a Delivery. Includes information that is useful to show to the student
    when they make the delivery.

    This is almost the same as the ``aggregated_groupinfo`` API, except we
    exclude ``deadlines`` for efficiency reasons.
    """
    resource = MinimalGroupResource
