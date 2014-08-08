from django.contrib.auth.models import User
from django.db.models import Q
from djangorestframework.views import ListModelView
from djangorestframework.resources import ModelResource
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.permissions import BasePermission
from djangorestframework.response import ErrorResponse
from djangorestframework import status

from devilry.apps.core.models.devilryuserprofile import user_is_admin_or_superadmin



class IsAnyAdmin(BasePermission):
    """
    Djangorestframework permission checker that checks if the requesting user
    has admin-permissions on anything.
    """
    def check_permission(self, user):
        if not user_is_admin_or_superadmin(user):
            raise ErrorResponse(status.HTTP_403_FORBIDDEN,
                                {'detail': 'Only administrators have permission to query the user database.'})

class UserResource(ModelResource):
    fields = ('id', 'username', 'email', 'full_name', 'languagecode')
    model = User

    def full_name(self, instance):
        return instance.devilryuserprofile.full_name

    def languagecode(self, instance):
        return instance.devilryuserprofile.languagecode


class SearchForUsers(ListModelView):
    """
    Provides an API suited for autocompleting users.

    # GET
    Search for users by:

    - Full name
    - Username
    - Email

    Uses case-ignore-contains search.

    ## Parameters
    The search is specified in the ``query`` parameter in the querystring.

    ## Response
    A list of 0 to 10 users with the following attributes for each user:

    - ``id`` (internal Devilry ID)
    - ``username``
    - ``full_name``
    - ``email``
    - ``languagecode`` (preferred language)

    If the ``query`` has less than 3 characters, and empty list is returned.
    """
    resource = UserResource
    permissions = (IsAuthenticated, IsAnyAdmin)

    #: Minimum number of characters allowed in the search
    minimum_characters = 2

    #: Maximum number of items to return
    response_limit = 10

    def get_queryset(self):
        querystring = self.request.GET.get('query', '')
        if len(querystring) <= self.minimum_characters:
            return User.objects.none()
        qry = User.objects.filter(Q(username__icontains=querystring) |
                                  Q(email__icontains=querystring) |
                                  Q(devilryuserprofile__full_name__icontains=querystring))
        qry = qry.select_related('devilryuserprofile')
        return qry[:self.response_limit]
