# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.test import testcases
from model_mommy import mommy

from devilry.apps.core import mommy_recipes


class TestAPIKey(testcases.TestCase):

    def test_key_length(self):
        testkey = mommy.make('devilry_api.APIKey')
        self.assertEqual(40, len(testkey.key))

    def test_key_has_expired(self):
        testkey = mommy.make('devilry_api.APIKey', created_datetime=mommy_recipes.OLD_PERIOD_START)
        self.assertTrue(testkey.has_expired)

    def test_key_has_not_expired(self):
        testkey = mommy.make('devilry_api.APIKey', created_datetime=mommy_recipes.FUTURE_PERIOD_START)
        self.assertFalse(testkey.has_expired)
