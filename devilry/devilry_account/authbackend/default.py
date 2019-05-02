from django.contrib import auth
from django.contrib.auth import get_user_model


class AbstractBaseAuthBackend(object):
    def get_user(self, user_id):
        """
        locate and return a :class:`User` based on the ``primary key`` of the current :class:`User` model.

        NOTE: this function is defined by Django as required for an Auth-backend

        :param user_id: the ``id`` of a :class:`User`
        :return: the ``User`` matching the given ``user_id`` if it exists, ``None`` if not.
        """
        try:
            return auth.get_user_model().objects.get(pk=user_id)
        except auth.get_user_model().DoesNotExist:
            return None


class EmailAuthBackend(AbstractBaseAuthBackend):
    """
    An authentication backend that authenticates a user by email.
    """

    def authenticate(self, request, password, email):
        """
        Find the `User` corresponding to ``email``, verify ``password`` and return user.

        NOTE: this function is defined by Django as required for an Auth-backend

        Parameters:
            password (str): ``password`` for the user to authenticate
            email (str): ``email`` for the user to authenticate

        Returns:
            User: The authenticated user if authentication was successful, or ``None`` if not.
        """
        try:
            user = self.lookup_user(email=email)
        except get_user_model().DoesNotExist:
            return None
        else:
            if user.check_password(raw_password=password):
                return user
            else:
                return None

    def lookup_user(self, email):
        user = get_user_model().objects.get_by_email(email=email)
        return user


class UsernameAuthBackend(AbstractBaseAuthBackend):
    """
    An authentication backend that authenticates a user by username.
    """

    def authenticate(self, request, password, username):
        """
        Find the `User` corresponding to ``username``, verify ``password`` and return user.

        NOTE: this function is defined by Django as required for an Auth-backend

        Parameters:
            password (str): ``password`` for the user to authenticate
            username (str): ``username`` for the user to authenticate

        Returns:
            User: The authenticated user if authentication was successful, or ``None`` if not.
        """
        try:
            user = self.lookup_user(username=username)
        except get_user_model().DoesNotExist:
            return None
        else:
            if user.check_password(raw_password=password):
                return user
            else:
                return None

    def lookup_user(self, username):
        user = get_user_model().objects.get_by_username(username=username)
        return user
