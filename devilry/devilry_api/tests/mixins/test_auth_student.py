from devilry.devilry_api.tests.mixins import test_auth_common
from model_mommy import mommy

from devilry.apps.core import mommy_recipes
from devilry.devilry_api import devilry_api_mommy_factories


class TestAuthAPIKeyStudentMixin(test_auth_common.TestAuthAPIKeyMixin):
    """
    Mixin for testing the student role
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
