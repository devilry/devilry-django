from django.test import TestCase
from cradmin_legacy.apps.cradmin_authenticate import backends
from unittest import mock

from cradmin_legacy.tests.views.helpers import create_testuser


class TestEmailAuthBackend(TestCase):
    def setUp(self):
        self.testuser = create_testuser(username="testuser", password="test", email="test@example.com")
        self.emailauthbackend = backends.EmailAuthBackend()

    def test_get_user_from_email(self):
        user = self.emailauthbackend._EmailAuthBackend__get_user_from_email(self.testuser.email)
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.testuser.pk)

    def test_get_user_from_email_returns_none(self):
        user = self.emailauthbackend._EmailAuthBackend__get_user_from_email("doesnotexist@example.com")
        self.assertIsNone(user)

    def test_get_user(self):
        user = self.emailauthbackend.get_user(self.testuser.pk)
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.testuser.pk)

    def test_get_user_returns_none(self):
        user = self.emailauthbackend.get_user(42)
        self.assertIsNone(user)

    def test_authenticate(self):
        user = self.emailauthbackend.authenticate(request=mock.MagicMock(), email=self.testuser.email, password="test")
        self.assertIsNotNone(user)
        self.assertEqual(self.testuser.pk, user.pk)

    def test_authenticate_invalid_password_returns_none(self):
        user = self.emailauthbackend.authenticate(
            request=mock.MagicMock(), email=self.testuser.email, password="notcorrectpassword"
        )
        self.assertIsNone(user)

    def test_authenticate_invalid_email_returns_none(self):
        user = self.emailauthbackend.authenticate(
            request=mock.MagicMock(), email="doesnotexist@example.com", password="test"
        )
        self.assertIsNone(user)
