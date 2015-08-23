from django.test import TestCase
from devilry.devilry_account.authbackend.default import EmailAuthBackend
from devilry.devilry_account.models import User


class TestEmailAuthBackend(TestCase):
    def setUp(self):
        self.testuser = User.objects.create_user(
            email='testuser@example.com',
            password='test')
        self.authbackend = EmailAuthBackend()

    def test_lookup_user(self):
        user = self.authbackend.lookup_user(email=self.testuser.email)
        self.assertEquals(user.pk, self.testuser.pk)

    def test_lookup_user_invalid_email(self):
        with self.assertRaises(User.DoesNotExist):
            self.authbackend.lookup_user(email='invalid@example.com')

    def test_get_user(self):
        user = self.authbackend.get_user(self.testuser.pk)
        self.assertEquals(user.pk, self.testuser.pk)

    def test_get_user_returns_none(self):
        user = self.authbackend.get_user(42)
        self.assertIsNone(user)

    def test_authenticate(self):
        user = self.authbackend.authenticate(email=self.testuser.email,
                                             password='test')
        self.assertIsNotNone(user)
        self.assertEquals(self.testuser.pk, user.pk)

    def test_authenticate_invalid_password_returns_none(self):
        user = self.authbackend.authenticate(email=self.testuser.email,
                                             password='notcorrectpassword')
        self.assertIsNone(user)

    def test_authenticate_invalid_email_returns_none(self):
        user = self.authbackend.authenticate(email='doesnotexist@example.com',
                                             password='test')
        self.assertIsNone(user)
