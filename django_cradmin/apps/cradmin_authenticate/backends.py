from builtins import object
from django.contrib import auth
from django.contrib.auth.hashers import check_password


class EmailAuthBackend(object):
    """
    Custom Authentication backend for using `email` as your login-field on any ``User``-model. This will also work with
    the default django ``User``-model, as it does not require ``USERNAME_FIELD`` to be ``email``.
    """

    def authenticate(self, request, email=None, password=None):
        """
        Find the `User` corresponding to ``email``, verify ``password`` and return user.

        NOTE: this function is defined by Django as required for an Auth-backend

        :param email: ``email`` for the user to authenticate
        :param password: ``password`` for the user to authenticate
        :return: the ``User`` if authentication was successful, or ``None`` if not.
        """
        if not email or not password:
            return None
        user = self.__get_user_from_email(email)
        if not user:
            return None

        password_valid = check_password(password, user.password)

        if not password_valid:
            return None

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

    def __get_user_from_email(self, email):
        """
        locate and return a :class:`User` based on the ``email``-field of the current :class:`User` model.

        this is simply a utility for ``authenticate()``

        :param email: the ``email``-field of a ``User``
        :return: the ``User`` matching the given ``email`` if it exists, ``None`` if not.
        """
        user_model = auth.get_user_model()
        try:
            return user_model.objects.get(email=email)
        except user_model.DoesNotExist:
            return None
