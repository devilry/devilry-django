from djangorestframework.permissions import BasePermission
from djangorestframework.response import ErrorResponse
from djangorestframework import status

from devilry.apps.core.models import AssignmentGroup


def format_datetime(datetime):
    return datetime.strftime('%Y-%m-%d %H:%M:%S')

def format_timedelta(td):
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return {'days': abs(td.days),
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds}

class GroupResourceHelpersMixin(object):
    def format_user(self, user):
        return {'email': user.email,
                'username': user.username,
                'id': user.id,
                'full_name': user.devilryuserprofile.full_name,
                'displayname': user.devilryuserprofile.full_name or user.username}

    def format_candidate(self, candidate):
        cand = {'id': candidate.id,
                'user': self.format_user(candidate.student),
                'candidate_id': candidate.candidate_id,
                'identifier': candidate.identifier}
        return cand

    def format_basenode(self, basenode):
        return {'id': basenode.id,
                'short_name': basenode.short_name,
                'long_name': basenode.long_name}


class IsPublishedAndCandidate(BasePermission):
    """
    Djangorestframework permission checker that checks if the requesting user
    is candidate on the requested group.
    """
    def check_permission(self, user):
        groupid = self.view.kwargs['id']
        try:
            AssignmentGroup.published_where_is_candidate(user).get(id=groupid)
        except AssignmentGroup.DoesNotExist, e:
            raise ErrorResponse(status.HTTP_403_FORBIDDEN,
                                {'detail': 'Only candidates on group with ID={0} can make this request.'.format(groupid)})
