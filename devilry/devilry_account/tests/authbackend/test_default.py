from django.test import TestCase
from devilry.devilry_account.authbackend.default import EmailAuthBackend, UsernameAuthBackend
from devilry.devilry_account.models import User


class TestEmailAuthBackend(TestCase):
    def setUp(self):
        self.testuser = User.objects.create_user(
            email='testuser@example.com',
            password='test')
        self.authbackend = EmailAuthBackend()

    def test_lookup_user(self):
        user = self.authbackend.lookup_user(email='testuser@example.com')
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
        user = self.authbackend.authenticate(email='testuser@example.com',
                                             password='test')
        self.assertIsNotNone(user)
        self.assertEquals(self.testuser.pk, user.pk)

    def test_authenticate_invalid_password_returns_none(self):
        user = self.authbackend.authenticate(email='testuser@example.com',
                                             password='notcorrectpassword')
        self.assertIsNone(user)

    def test_authenticate_invalid_email_returns_none(self):
        user = self.authbackend.authenticate(email='doesnotexist@example.com',
                                             password='test')
        self.assertIsNone(user)


class TestUsernameAuthBackend(TestCase):
    def setUp(self):
        self.testuser = User.objects.create_user(
            username='testuser',
            password='test')
        self.authbackend = UsernameAuthBackend()

    def test_lookup_user(self):
        user = self.authbackend.lookup_user(username='testuser')
        self.assertEquals(user.pk, self.testuser.pk)

    def test_lookup_user_invalid_email(self):
        with self.assertRaises(User.DoesNotExist):
            self.authbackend.lookup_user(username='invalid')

    def test_get_user(self):
        user = self.authbackend.get_user(self.testuser.pk)
        self.assertEquals(user.pk, self.testuser.pk)

    def test_get_user_returns_none(self):
        user = self.authbackend.get_user(42)
        self.assertIsNone(user)

    def test_authenticate(self):
        user = self.authbackend.authenticate(username='testuser',
                                             password='test')
        self.assertIsNotNone(user)
        self.assertEquals(self.testuser.pk, user.pk)

    def test_authenticate_invalid_password_returns_none(self):
        user = self.authbackend.authenticate(username='testuser',
                                             password='notcorrectpassword')
        self.assertIsNone(user)

    def test_authenticate_invalid_email_returns_none(self):
        user = self.authbackend.authenticate(username='doesnotexist',
                                             password='test')
        self.assertIsNone(user)
