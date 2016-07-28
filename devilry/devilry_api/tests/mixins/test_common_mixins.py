# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.utils import timezone

from devilry.apps.core import mommy_recipes
from devilry.devilry_api.models import APIKey


class TestAuthAPIKeyMixin(object):
    """
    These test cases will only test for the read permission level
    which is the lowest.

    Examples:
        class TestCase(TestAuthAPIKeyMixin,
                       api_test_helper.TestCaseMixin,
                       APITestCase):
            viewclass = MyView
    """

    #: This can be useful if we have a variables in the url path
    test_auth_apikey_mixin_extra_kwargs = {}

    def get_apikey(self, **kwargs):
        """
        should return a :obj:`~devilry_api.APIKey`
        Returns:
            :obj:`~devilry_api.APIKey`

        """
        raise NotImplementedError()

    def test_auth_not_valid_api_key(self):
        response = self.mock_get_request(apikey='invalid', **self.test_auth_apikey_mixin_extra_kwargs)
        self.assertEqual(401, response.status_code)

    def test_auth_key_expired(self):
        apikey = self.get_apikey(created_datetime=mommy_recipes.OLD_PERIOD_START)
        response = self.mock_get_request(apikey=apikey.key, **self.test_auth_apikey_mixin_extra_kwargs)
        self.assertEqual(401, response.status_code)

    def test_key_expired_short(self):
        apikey = self.get_apikey(created_datetime=timezone.now()-APIKey.LIFETIME[APIKey.LIFETIME_SHORT])
        response = self.mock_get_request(apikey=apikey.key, **self.test_auth_apikey_mixin_extra_kwargs)
        self.assertEqual(401, response.status_code)

    def test_key_expired_long(self):
        apikey = self.get_apikey(created_datetime=timezone.now()-APIKey.LIFETIME[APIKey.LIFETIME_LONG])
        response = self.mock_get_request(apikey=apikey.key, **self.test_auth_apikey_mixin_extra_kwargs)
        self.assertEqual(401, response.status_code)


class TestReadOnlyPermissionMixin(object):
    """
    Test mixin for read only permission.

    get_apikey() should return a key with read only permission

    Examples:
        class TestCase(TestReadOnlyPermissionMixin,
                       TestAuthAPIKeyMixin,
                       api_test_helper.TestCaseMixin,
                       APITestCase):
            viewclass = MyView
    """

    def test_post_403(self):
        apikey = self.get_apikey()
        response = self.mock_post_request(apikey=apikey.key)
        self.assertEqual(403, response.status_code)

    def test_delete_403(self):
        apikey = self.get_apikey()
        response = self.mock_delete_request(apikey=apikey.key)
        self.assertEqual(403, response.status_code)

    def test_put_403(self):
        apikey = self.get_apikey()
        response = self.mock_put_request(apikey=apikey.key)
        self.assertEqual(403, response.status_code)

    def test_patch_403(self):
        apikey = self.get_apikey()
        response = self.mock_patch_request(apikey=apikey.key)
        self.assertEqual(403, response.status_code)