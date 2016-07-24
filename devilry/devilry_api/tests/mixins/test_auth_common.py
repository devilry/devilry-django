# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from devilry.apps.core import mommy_recipes


class TestAuthAPIKeyMixin(object):

    def get_apikey(self, **kwargs):
        """
        should return a :obj:`~devilry_api.APIKey`
        Returns:
            :obj:`~devilry_api.APIKey`

        """
        raise NotImplementedError()

    def test_auth_not_valid_api_key(self):
        response = self.mock_get_request(apikey='b2660057e2a109c032aa07171633d4fb92ca560a')
        self.assertEqual(401, response.status_code)

    def test_auth_api_key(self):
        api_key = self.get_apikey()
        response = self.mock_get_request(apikey=api_key.key)
        self.assertEqual(200, response.status_code)

    def test_auth_key_expired(self):
        api_key = self.get_apikey(created_datetime=mommy_recipes.OLD_PERIOD_START)
        response = self.mock_get_request(apikey=api_key.key)
        self.assertEqual(401, response.status_code)
