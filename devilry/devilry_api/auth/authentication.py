# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy
from rest_framework import authentication

from devilry.devilry_api.models import APIKey


class TokenAuthentication(authentication.TokenAuthentication):
    model = APIKey

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'token':
            msg = ugettext_lazy('Token not provided.')
            raise authentication.exceptions.AuthenticationFailed(msg)

        if len(auth) == 1:
            msg = ugettext_lazy('Invalid token header. No credentials provided.')
            raise authentication.exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = ugettext_lazy('Invalid token header. Token string should not contain spaces.')
            raise authentication.exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = ugettext_lazy('Invalid token header. Token string should not contain invalid characters.')
            raise authentication.exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        model = self.get_model()

        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise authentication.exceptions.AuthenticationFailed(ugettext_lazy('Invalid token.'))

        if not token.user.is_active:
            raise authentication.exceptions.AuthenticationFailed(ugettext_lazy('User inactive or deleted.'))

        if token.has_expired:
            raise authentication.exceptions.AuthenticationFailed(ugettext_lazy('Api key has expired.'))

        if not token.is_active:
            raise authentication.exceptions.AuthenticationFailed(ugettext_lazy('Api key is not active.'))

        return (token.user, token)
