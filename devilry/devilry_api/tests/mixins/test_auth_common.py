# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from model_mommy import mommy

from devilry.apps.core import mommy_recipes


class TestAuthAPIKeyMixin(object):

    def get_user(self):
        """
        should return a user
        Returns:
            :obj:`~devilry_account.User`

        """
        raise NotImplementedError()

    def test_auth_not_valid_api_key(self):
        response = self.mock_get_request(apikey='b2660057e2a109c032aa07171633d4fb92ca560a')
        self.assertEqual(401, response.status_code)

    def test_auth_api_key(self):
        api_key = mommy.make('devilry_api.APIKey',
                             user=self.get_user(),
                             expiration_date=mommy_recipes.ACTIVE_PERIOD_END)
        response = self.mock_get_request(apikey=api_key.key)
        self.assertEqual(200, response.status_code)

    def test_auth_key_expired(self):
        api_key = mommy.make('devilry_api.APIKey',
                             user=self.get_user(),
                             expiration_date=mommy_recipes.OLD_PERIOD_END)
        response = self.mock_get_request(apikey=api_key.key)
        self.assertEqual(401, response.status_code)

    def test_auth_key_not_expired_none(self):
        api_key = mommy.make('devilry_api.APIKey',
                             user=self.get_user(),
                             expiration_date=None)
        response = self.mock_get_request(apikey=api_key.key)
        self.assertEqual(200, response.status_code)

    def test_auth_key_not_active_expiration_none(self):
        api_key = mommy.make('devilry_api.APIKey',
                             user=self.get_user(),
                             start_datetime=mommy_recipes.FUTURE_PERIOD_START,
                             expiration_date=None)
        response = self.mock_get_request(apikey=api_key.key)
        self.assertEqual(401, response.status_code)

    def test_key_is_not_active(self):
        api_key = mommy.make('devilry_api.APIKey',
                             user=self.get_user(),
                             start_datetime=mommy_recipes.OLD_PERIOD_START,
                             expiration_date=mommy_recipes.OLD_PERIOD_END)
        response = self.mock_get_request(apikey=api_key.key)
        self.assertEqual(401, response.status_code)

    def test_auth_key_active(self):
        api_key = mommy.make('devilry_api.APIKey',
                             user=self.get_user(),
                             start_datetime=mommy_recipes.ACTIVE_PERIOD_START,
                             expiration_date=mommy_recipes.ACTIVE_PERIOD_END)
        response = self.mock_get_request(apikey=api_key.key)
        self.assertEqual(200, response.status_code)
