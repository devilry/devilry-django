# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.test import testcases
from model_mommy import mommy
from django.utils import timezone

from devilry.apps.core import mommy_recipes
from devilry.devilry_api.models import APIKey


class TestAPIKey(testcases.TestCase):

    def test_key_length(self):
        with self.settings(DEVILRY_API_KEYLENGTH=40):
            testkey = mommy.make('devilry_api.APIKey')
            self.assertEqual(40, len(testkey.key))

    def test_key_has_expired(self):
        testkey = mommy.make('devilry_api.APIKey', created_datetime=mommy_recipes.OLD_PERIOD_START)
        self.assertTrue(testkey.has_expired)

    def test_key_has_not_expired(self):
        testkey = mommy.make('devilry_api.APIKey')
        self.assertFalse(testkey.has_expired)

    def test_key_has_expired_short(self):
        testkey = mommy.make('devilry_api.APIKey',
                             created_datetime=timezone.now() - APIKey.LIFETIME[APIKey.LIFETIME_SHORT])
        self.assertTrue(testkey.has_expired)

    def test_key_has_expired_long(self):
        testkey = mommy.make('devilry_api.APIKey',
                             created_datetime=timezone.now() - APIKey.LIFETIME[APIKey.LIFETIME_LONG],
                             keytype=APIKey.LIFETIME_LONG)
        self.assertTrue(testkey.has_expired)

    def test_key_has_student_permission_only(self):
        testkey = mommy.make('devilry_api.APIKey', student_permission=APIKey.STUDENT_PERMISSION_READ)
        self.assertTrue(testkey.has_student_permission)
        self.assertFalse(testkey.has_examiner_permission)
        self.assertFalse(testkey.has_admin_permission)

    def test_key_has_examiner_permission_only(self):
        testkey = mommy.make('devilry_api.APIKey', examiner_permission=APIKey.EXAMINER_PERMISSION_READ)
        self.assertTrue(testkey.has_examiner_permission)
        self.assertFalse(testkey.has_admin_permission)
        self.assertFalse(testkey.has_student_permission)

    def test_key_has_admin_permission_only(self):
        testkey = mommy.make('devilry_api.APIKey', admin_permission=APIKey.ADMIN_PERMISSION_READ)
        self.assertTrue(testkey.has_admin_permission)
        self.assertFalse(testkey.has_examiner_permission)
        self.assertFalse(testkey.has_student_permission)
