from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated

from devilry.apps.core.models.devilryuserprofile import user_is_nodeadmin
from devilry.apps.core.models.devilryuserprofile import user_is_subjectadmin
from devilry.apps.core.models.devilryuserprofile import user_is_periodadmin
from devilry.apps.core.models.devilryuserprofile import user_is_assignmentadmin
from devilry.apps.core.models.devilryuserprofile import user_is_student
from devilry.apps.core.models.devilryuserprofile import user_is_examiner




class UserInfo(View):
    """
    Provides an API that lists information about the authenticated user.

    # GET
    An object with the following attributes:

    - ``id`` (int): Internal Devilry ID. Is never ``null``, and unlike the username, this is never changed.
    - ``username`` (string): The unique Devilry username for this user. Is never ``null``, however it may be changed by a superuser.
    - ``full_name`` (string|null): The full name of the user.
    - ``email`` (string|null): The email address of the user.
    - ``languagecode`` (string|null): The languagecode of the preferred language.
    - ``is_superuser`` (boolean): Is the user a superuser?
    - ``is_nodeadmin`` (boolean): Is the user admin directly on any Node?
    - ``is_subjectadmin`` (boolean): Is the user admin directly on any Subject?
    - ``is_periodadmin`` (boolean): Is the user admin directly on any Period?
    - ``is_assignmentadmin`` (boolean): Is the user admin directly on any Assignment?
    - ``is_student`` (boolean): Is the user candidate on any AssignmentGroup?
    - ``is_examiner`` (boolean): Is the user examiner on any AssignmentGroup?
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
                'is_assignmentadmin': user_is_assignmentadmin(user),
                'is_student': user_is_student(user),
                'is_examiner': user_is_examiner(user)
               }
