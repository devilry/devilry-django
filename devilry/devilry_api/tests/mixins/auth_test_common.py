# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django import test
from model_mommy import mommy

from devilry.apps.core import mommy_recipes
from devilry.devilry_api.tests.mixins import api_test_helper


class TestAuthMixin(api_test_helper.TestCaseMixin, test.TestCase):

    def test_auth_no_api_key(self):
        response = self.mock_get_request()
        self.assertEqual(401, response.status_code)

    def test_auth_api_key(self):
        api_key = mommy.make('devilry_api.APIKey',
                             expiration_date=mommy_recipes.ACTIVE_PERIOD_END)
        response = self.mock_get_request(apikey='Token {}'.format(api_key.key))
        self.assertEqual(200, response.status_code)

    def test_auth_key_expired(self):
        api_key = mommy.make('devilry_api.APIKey',
                             expiration_date=mommy_recipes.OLD_PERIOD_END)
        response = self.mock_get_request(apikey='Token {}'.format(api_key.key))
        self.assertEqual(401, response.status_code)

    def test_auth_key_not_expired_none(self):
        api_key = mommy.make('devilry_api.APIKey',
                             expiration_date=None)
        response = self.mock_get_request(apikey='Token {}'.format(api_key.key))
        self.assertEqual(200, response.status_code)

    def test_auth_key_not_active_expiration_none(self):
        api_key = mommy.make('devilry_api.APIKey',
                             start_datetime=mommy_recipes.FUTURE_PERIOD_START,
                             expiration_date=None)
        response = self.mock_get_request(apikey='Token {}'.format(api_key.key))
        self.assertEqual(401, response.status_code)

    def test_key_is_not_active(self):
        api_key = mommy.make('devilry_api.APIKey',
                             start_datetime=mommy_recipes.OLD_PERIOD_START,
                             expiration_date=mommy_recipes.OLD_PERIOD_END)

        response = self.mock_get_request(apikey='Token {}'.format(api_key.key))
        self.assertEqual(401, response.status_code)

    def test_auth_key_active(self):
        api_key = mommy.make('devilry_api.APIKey',
                             start_datetime=mommy_recipes.ACTIVE_PERIOD_START,
                             expiration_date=mommy_recipes.ACTIVE_PERIOD_END)

        response = self.mock_get_request(apikey='Token {}'.format(api_key.key))
        self.assertEqual(200, response.status_code)