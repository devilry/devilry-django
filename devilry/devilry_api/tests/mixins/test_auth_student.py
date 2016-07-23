from devilry.devilry_api.tests.mixins import test_auth_common
from model_mommy import mommy

from devilry.apps.core import mommy_recipes


class TestAuthAPIKeyStudentMixin(test_auth_common.TestAuthAPIKeyMixin):

    def get_user(self):
        """
        returns a studnet user
        Returns:
            :obj:`~devilry_account.User`

        """
        assignment = mommy.make('core.Assignment',
                                parentnode__parentnode__short_name='duckduck1010')
        candidate = mommy.make('core.Candidate',
                               relatedstudent=mommy.make('core.RelatedStudent'),
                               assignment_group__parentnode=assignment)
        return candidate.relatedstudent.user

    def test_auth_not_student(self):
        api_key = mommy.make('devilry_api.APIKey',
                             expiration_date=mommy_recipes.ACTIVE_PERIOD_END)
        response = self.mock_get_request(apikey=api_key.key)
        self.assertEqual(403, response.status_code)
