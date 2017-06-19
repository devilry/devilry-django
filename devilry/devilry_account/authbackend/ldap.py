from django.contrib import auth
from django.contrib.auth import get_user_model
from django_auth_ldap.backend import LDAPBackend


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

class LDAPUsernameAuthBackend(LDAPBackend):
    """
    An authentication backend that authenticates a user by username.
    """

    # TODO Override get_or_create_user
    def lookup_user(self, username):
        user = get_user_model().objects.get_by_username(username=username)
        return user

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