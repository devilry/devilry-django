from django.contrib.auth.models import User

from devilry.simplified import InvalidUsername


def _convert_list_of_usernames_to_userobjects(usernames):
    """
    Parse list of usernames to list of User objects. Each username must be an existing user.

    If all usernames are valid, usernames are returned.
    """
    users = []
    for username in usernames:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise InvalidUsername(username)
        users.append(user)
    return users
