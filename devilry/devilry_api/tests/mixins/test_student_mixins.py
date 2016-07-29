from devilry.devilry_api import devilry_api_mommy_factories
from test_common_mixins import TestAuthAPIKeyMixin


class TestAuthAPIKeyStudentMixin(TestAuthAPIKeyMixin):
    """
    These test cases will only test for the read permission level
    which is the lowest.

    Examples:
        class TestCase(TestAuthAPIKeyStudentMixin,
                       test_auth_common.TestAuthAPIKeyMixin,
                       api_test_helper.TestCaseMixin,
                       APITestCase):
            viewclass = MyView
    """
    
    def get_apikey(self, **kwargs):
        """
        returns a :obj:`~devilry_api.APIKey` with student permission
        Returns:
            :obj:`~devilry_api.APIKey`

        """
        return devilry_api_mommy_factories.api_key_student_permission_read(**kwargs)

    def test_auth_not_student(self):
        api_key = devilry_api_mommy_factories.api_key_short_lifetime()
        response = self.mock_get_request(apikey=api_key.key)
        self.assertEqual(403, response.status_code)

    def test_auth_examiner_permission_not_student(self):
        api_key = devilry_api_mommy_factories.api_key_examiner_permission_read()
        response = self.mock_get_request(apikey=api_key.key)
        self.assertEqual(403, response.status_code)

    def test_auth_admin_permission_not_student(self):
        api_key = devilry_api_mommy_factories.api_key_admin_permission_read()
        response = self.mock_get_request(apikey=api_key.key)
        self.assertEqual(403, response.status_code)
