from django.core import mail

from django.test import TestCase
from cradmin_legacy.python2_compatibility import mock

from cradmin_legacy.apps.cradmin_invite.invite_url import InviteUrl
from cradmin_legacy.tests.helpers import create_user


class InviteUrlMock(InviteUrl):
    def get_appname(self):
        return "testapp"

    def get_confirm_invite_url(self, token):
        return f"/invite/accept/{token.token}"


class InviteUrlWithStaticTokenMock(InviteUrlMock):
    def generate_generictoken(self, email=None):
        testtoken = mock.MagicMock()
        testtoken.token = "test-token"
        return testtoken


class InviteUrlWithTokenIteratorMock(InviteUrlMock):
    def __init__(self, *args, **kwargs):
        self.tokens = iter(["token1", "token2", "token3"])
        super().__init__(*args, **kwargs)

    def _generate_generictoken(self, email=None):
        testtoken = mock.MagicMock()
        testtoken.token = next(self.tokens)
        return testtoken


class TestSendActivationEmail(TestCase):
    def setUp(self):
        self.testuser = create_user("testuser", email="testuser@example.com")

        # Any object will work as the target of invites.
        # We use a user object since we have that easily available
        self.invite_target = create_user("invitetarget")

    def test_generate_generictoken(self):
        token = InviteUrlMock(
            request=mock.MagicMock(), private=True, content_object=self.invite_target
        ).generate_generictoken()
        self.assertEqual(token.content_object, self.invite_target)

    def test_generate_generictoken_with_email(self):
        token = InviteUrlMock(
            request=mock.MagicMock(), private=True, content_object=self.invite_target
        ).generate_generictoken(email="test@example.com")
        self.assertEqual(token.metadata["email"], "test@example.com")

    def test_generate_generictoken_with_email_and_metadata(self):
        token = InviteUrlMock(
            request=mock.MagicMock(), private=True, content_object=self.invite_target, metadata={"test": 10}
        ).generate_generictoken(email="test@example.com")
        self.assertEqual(token.metadata["email"], "test@example.com")
        self.assertEqual(token.metadata["test"], 10)

    def test_generate_generictoken_with_email_and_metadata_with_email(self):
        token = InviteUrlMock(
            request=mock.MagicMock(),
            private=True,
            content_object=self.invite_target,
            metadata={"email": "existing@example.com"},
        ).generate_generictoken(email="test@example.com")
        self.assertEqual(token.metadata["email"], "existing@example.com")

    def test_send_email(self):
        testrequest = mock.MagicMock()
        testrequest.build_absolute_uri = lambda path: f"http://testserver{path}"

        with self.settings(CRADMIN_LEGACY_SITENAME="Testsite"):
            InviteUrlWithStaticTokenMock(
                request=testrequest, content_object=self.invite_target, private=True
            ).send_email("test@example.com")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Invitation to Testsite")
        self.assertIn("http://testserver/invite/accept/test-token", mail.outbox[0].alternatives[0][0])
        self.assertIn("Click the button below to accept the invite.", mail.outbox[0].alternatives[0][0])

    def test_send_email_private(self):
        testrequest = mock.MagicMock()
        testrequest.build_absolute_uri = lambda path: f"http://testserver{path}"

        with self.settings(CRADMIN_LEGACY_SITENAME="Testsite"):
            inviteurl = InviteUrlWithTokenIteratorMock(
                request=testrequest, content_object=self.invite_target, private=True
            )
            inviteurl.send_email("test1@example.com", "test2@example.com", "test3@example.com")
        self.assertIn("token1", mail.outbox[0].body)
        self.assertIn("token2", mail.outbox[1].body)
        self.assertIn("token3", mail.outbox[2].body)

    def test_send_email_public(self):
        testrequest = mock.MagicMock()
        testrequest.build_absolute_uri = lambda path: f"http://testserver{path}"

        with self.settings(CRADMIN_LEGACY_SITENAME="Testsite"):
            inviteurl = InviteUrlWithTokenIteratorMock(
                request=testrequest, content_object=self.invite_target, private=False
            )
            inviteurl.send_email("test1@example.com", "test2@example.com", "test3@example.com")
        self.assertIn("token1", mail.outbox[0].body)
        self.assertIn("token1", mail.outbox[1].body)
        self.assertIn("token1", mail.outbox[2].body)

    def test_get_share_url(self):
        testrequest = mock.MagicMock()
        testrequest.build_absolute_uri = lambda path: f"http://testserver{path}"
        self.assertEqual(
            InviteUrlWithStaticTokenMock(
                request=testrequest, private=True, content_object=self.invite_target
            ).get_share_url(),
            "http://testserver/invite/accept/test-token",
        )

    def test_get_share_url_private(self):
        testrequest = mock.MagicMock()
        testrequest.build_absolute_uri = lambda path: f"http://testserver{path}"
        inviteurl = InviteUrlWithTokenIteratorMock(request=testrequest, private=True, content_object=self.invite_target)
        self.assertEqual(inviteurl.get_share_url(), "http://testserver/invite/accept/token1")
        self.assertEqual(inviteurl.get_share_url(), "http://testserver/invite/accept/token2")
        self.assertEqual(inviteurl.get_share_url(), "http://testserver/invite/accept/token3")

    def test_get_share_url_public(self):
        testrequest = mock.MagicMock()
        testrequest.build_absolute_uri = lambda path: f"http://testserver{path}"
        inviteurl = InviteUrlWithTokenIteratorMock(
            request=testrequest, private=False, content_object=self.invite_target
        )
        self.assertEqual(inviteurl.get_share_url(), "http://testserver/invite/accept/token1")
        self.assertEqual(inviteurl.get_share_url(), "http://testserver/invite/accept/token1")
        self.assertEqual(inviteurl.get_share_url(), "http://testserver/invite/accept/token1")
