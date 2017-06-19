from django.contrib import auth
from django.contrib.auth import get_user_model
from django_auth_ldap.backend import LDAPBackend


class LDAPUsernameAuthBackend(LDAPBackend):
    """
    Devilry LDAP authentication backend that authenticates a user by username.
    """

    def get_or_create_user(self, username, ldap_user):
        """
        This must return a (User, created) 2-tuple for the given LDAP user.
        username is the Django-friendly username of the user. ldap_user.dn is
        the user's DN and ldap_user.attrs contains all of their LDAP attributes.
        """
        username = username.lower()
        cn = ldap_user.attrs.get('cn')
        fullname = ''
        if cn and isinstance(cn, list):
            fullname = cn[0]
        kwargs = {
            'username': username,
            'fullname': fullname
        }
        # import sys
        # print >> sys.stderr, 'LDAP attrs', ldap_user.attrs
        user, created = get_user_model().objects.get_or_create_user(**kwargs)
        if fullname and user.fullname != fullname:
            user.fullname = fullname
            user.clean()
            user.save()
        return user, created

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
