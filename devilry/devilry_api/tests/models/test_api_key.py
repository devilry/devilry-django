# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.test import testcases
from model_mommy import mommy

from devilry.apps.core import mommy_recipes


class TestAPIKey(testcases.TestCase):

    def test_key_length(self):
        testkey = mommy.make('devilry_api.APIKey')
        self.assertEqual(40, len(testkey.key))

    def test_key_expired(self):
        testkey = mommy.make('devilry_api.APIKey', expiration_date=mommy_recipes.OLD_PERIOD_START)
        self.assertTrue(testkey.has_expired)

    def test_key_not_expired(self):
        testkey = mommy.make('devilry_api.APIKey', expiration_date=mommy_recipes.ACTIVE_PERIOD_END)
        self.assertFalse(testkey.has_expired)

    def test_key_not_expired_expiration_none(self):
        testkey = mommy.make('devilry_api.APIKey', expiration_date=None)
        self.assertFalse(testkey.has_expired)

    def test_key_is_active_expiration_none(self):
        testkey = mommy.make('devilry_api.APIKey',
                             start_datetime=mommy_recipes.ACTIVE_PERIOD_START,
                             expiration_date=None)
        self.assertTrue(testkey.is_active)

    def test_key_is_active_expiration_is_set(self):
        testkey = mommy.make('devilry_api.APIKey',
                             start_datetime=mommy_recipes.ACTIVE_PERIOD_START,
                             expiration_date=mommy_recipes.ACTIVE_PERIOD_END)
        self.assertTrue(testkey.is_active)

    def test_key_is_not_active_expiration_none(self):
        testkey = mommy.make('devilry_api.APIKey',
                             start_datetime=mommy_recipes.FUTURE_PERIOD_START,
                             expiration_date=None)
        self.assertFalse(testkey.is_active)

    def test_key_is_not_active(self):
        testkey = mommy.make('devilry_api.APIKey',
                             start_datetime=mommy_recipes.FUTURE_PERIOD_START,
                             expiration_date=mommy_recipes.FUTURE_PERIOD_END)
        self.assertFalse(testkey.is_active)
