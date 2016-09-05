from devilry.devilry_api import devilry_api_mommy_factories as api_mommy
from test_common_mixins import TestAuthAPIKeyMixin


class TestAuthAPIKeyPeriodAdminMixin(TestAuthAPIKeyMixin):
    """
    These test cases will only test for the read permission level
    which is the lowest.

    Examples:
        class TestCase(TestAuthAPIKeyPeriodAdminMixin,
                       test_auth_common.TestAuthAPIKeyMixin,
                       api_test_helper.TestCaseMixin,
                       APITestCase):
            viewclass = MyView
    """

    def get_apikey(self, **kwargs):
        """
        return a :obj:`~devilry_api_APIKey` with admin permission read only
        Args:
            **kwargs:

        Returns:

        """
        return api_mommy.api_key_admin_permission_read(**kwargs)

    def test_auth_not_admin(self):
        api_key = api_mommy.api_key_short_lifetime()
        response = self.mock_get_request(apikey=api_key.key)
        self.assertEqual(403, response.status_code)

    def test_auth_student_permission_not_admin(self):
        api_key = api_mommy.api_key_student_permission_read()
        response = self.mock_get_request(apikey=api_key.key)
        self.assertEqual(403, response.status_code)

    def test_auth_examiner_permission_not_admin(self):
        api_key = api_mommy.api_key_examiner_permission_read()
        response = self.mock_get_request(apikey=api_key.key)
        self.assertEqual(403, response.status_code)
