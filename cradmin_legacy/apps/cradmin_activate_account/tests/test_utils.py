from django.core import mail

from django.test import TestCase
from cradmin_legacy.python2_compatibility import mock

from cradmin_legacy.apps.cradmin_activate_account.utils import ActivationEmail
from cradmin_legacy.tests.helpers import create_user


class TestSendActivationEmail(TestCase):
    def setUp(self):
        self.testuser = create_user("testuser", email="testuser@example.com")

    def test_generate_token(self):
        token = ActivationEmail(user=self.testuser, next_url="/", request=mock.MagicMock()).generate_token()
        self.assertEqual(token.metadata["next_url"], "/")

    def test_generate_token_no_next_url(self):
        with self.settings(LOGIN_URL="/next"):
            token = ActivationEmail(user=self.testuser, request=mock.MagicMock()).generate_token()
        self.assertEqual(token.metadata["next_url"], "/next")

    def test_send(self):
        testtoken = mock.MagicMock()
        testtoken.token = "test-token"
        testrequest = mock.MagicMock()
        testrequest.build_absolute_uri = lambda path: f"http://testserver{path}"

        with mock.patch.object(ActivationEmail, "generate_token", lambda s: testtoken):
            with self.settings(CRADMIN_LEGACY_SITENAME="Testsite"):
                ActivationEmail(user=self.testuser, request=testrequest).send()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Activate your Testsite account")
        self.assertIn(
            "http://testserver/cradmin_activate_account/activate/test-token", mail.outbox[0].alternatives[0][0]
        )
        self.assertIn(
            "Click the button below to activate your Testsite account, testuser.", mail.outbox[0].alternatives[0][0]
        )
