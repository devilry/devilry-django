# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from rest_framework import authentication

from devilry.devilry_api.models import APIKey


class TokenAuthentication(authentication.TokenAuthentication):
    model = APIKey
