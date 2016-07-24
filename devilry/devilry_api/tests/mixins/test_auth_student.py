from devilry.devilry_api.tests.mixins import test_auth_common
from model_mommy import mommy

from devilry.apps.core import mommy_recipes
from devilry.devilry_api import devilry_api_mommy_factories


class TestAuthAPIKeyStudentMixin(test_auth_common.TestAuthAPIKeyMixin):
    """
    These test cases will only test for the read permission level
    which is the lowest.
    """
    
    def get_apikey(self, **kwargs):
        """
        returns a :obj:`~devilry_api.APIKey` with student permission
        Returns:
            :obj:`~devilry_api.APIKey`

        """
        return devilry_api_mommy_factories.api_key_student_permission_read(**kwargs)

    def test_auth_not_student(self):
        self.set_up_common()
        api_key = devilry_api_mommy_factories.api_key_short_lifetime()
        response = self.mock_get_request(apikey=api_key.key, **self.extra_kwargs)
        self.assertEqual(403, response.status_code)

    def test_auth_examiner_permission_not_student(self):
        self.set_up_common()
        api_key = devilry_api_mommy_factories.api_key_examiner_permission_read()
        response = self.mock_get_request(apikey=api_key.key, **self.extra_kwargs)
        self.assertEqual(403, response.status_code)

    def test_auth_admin_permission_not_student(self):
        self.set_up_common()
        api_key = devilry_api_mommy_factories.api_key_admin_permission_read()
        response = self.mock_get_request(apikey=api_key.key, **self.extra_kwargs)
        self.assertEqual(403, response.status_code)
