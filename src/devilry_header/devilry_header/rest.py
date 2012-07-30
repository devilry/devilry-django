from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated

from devilry.apps.core.models.devilryuserprofile import user_is_nodeadmin
from devilry.apps.core.models.devilryuserprofile import user_is_subjectadmin
from devilry.apps.core.models.devilryuserprofile import user_is_periodadmin
from devilry.apps.core.models.devilryuserprofile import user_is_assignmentadmin




class UserInfo(View):
    """
    Provides an API that lists information about the authenticated user.

    # GET
    An object with the following attributes:

    - ``id`` (internal Devilry ID)
    - ``username``
    - ``full_name``
    - ``email``
    - ``languagecode`` (preferred language)
    - ``is_superuser``
    - ``is_nodeadmin``
    - ``is_subjectadmin``
    - ``is_periodadmin``
    - ``is_assignmentadmin``
    - ``is_student``
    - ``is_examiner``
    """
    permissions = (IsAuthenticated,)


    def get(self, request):
        user = self.request.user
        profile = user.devilryuserprofile
        return {'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': profile.full_name,
                'languagecode': profile.languagecode,
                'is_superuser': user.is_superuser,
                'is_nodeadmin': user_is_nodeadmin(user),
                'is_subjectadmin': user_is_subjectadmin(user),
                'is_periodadmin': user_is_periodadmin(user),
                'is_assignmentadmin': user_is_assignmentadmin(user)
               }
