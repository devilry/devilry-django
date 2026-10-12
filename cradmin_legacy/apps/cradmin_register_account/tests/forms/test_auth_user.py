from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from cradmin_legacy.apps.cradmin_register_account.forms.auth_user import (
    AuthUserCreateAccountForm,
    AuthUserCreateAccountAutoUsernameForm,
)
from cradmin_legacy.tests.helpers import create_user


class TestAuthUserCreateAccountForm(TestCase):
    def test_is_valid(self):
        form = AuthUserCreateAccountForm(
            {"username": "test", "password1": "test", "password2": "test", "email": "test@example.com"}
        )
        self.assertTrue(form.is_valid())

    def test_save(self):
        form = AuthUserCreateAccountForm(
            {"username": "test", "password1": "test", "password2": "test", "email": "test@example.com"}
        )
        form.is_valid()
        self.assertEqual(User.objects.count(), 0)
        form.save()
        self.assertEqual(User.objects.count(), 1)
        created_user = User.objects.first()
        self.assertEqual(created_user.username, "test")
        self.assertEqual(created_user.email, "test@example.com")
        self.assertTrue(created_user.has_usable_password())
        self.assertTrue(created_user.check_password("test"))

    def test_passwords_do_not_match(self):
        form = AuthUserCreateAccountForm(
            {"username": "unused", "password1": "test1", "password2": "test2", "email": "unused@example.com"}
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors(), ["The passwords do not match."])

    def test_email_is_not_unique(self):
        create_user("testuser", email="test@example.com")
        form = AuthUserCreateAccountForm(
            {"username": "unused", "password1": "unused", "password2": "unused", "email": "test@example.com"}
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {"email": ["Account with this email address already exists."]})

    def test_username_is_not_unique(self):
        create_user("test")
        form = AuthUserCreateAccountForm(
            {"username": "test", "password1": "unused", "password2": "unused", "email": "unused@example.com"}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("name already exists", form.errors["username"][0])


class TestAuthUserCreateAccountAutoUsernameForm(TestCase):
    def test_is_valid(self):
        form = AuthUserCreateAccountAutoUsernameForm(
            {"password1": "test", "password2": "test", "email": "test@example.com"}
        )
        self.assertTrue(form.is_valid())

    def test_save(self):
        form = AuthUserCreateAccountAutoUsernameForm(
            {"password1": "test", "password2": "test", "email": "test@example.com"}
        )
        form.is_valid()
        self.assertEqual(User.objects.count(), 0)
        form.save()
        self.assertEqual(User.objects.count(), 1)
        created_user = User.objects.first()
        self.assertEqual(created_user.username, "test@example.com")
        self.assertEqual(created_user.email, "test@example.com")
        self.assertTrue(created_user.has_usable_password())
        self.assertTrue(created_user.check_password("test"))

    def test_passwords_do_not_match(self):
        form = AuthUserCreateAccountAutoUsernameForm(
            {"password1": "test1", "password2": "test2", "email": "unused@example.com"}
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors(), ["The passwords do not match."])

    def test_email_is_not_unique(self):
        create_user("testuser", email="test@example.com")
        form = AuthUserCreateAccountAutoUsernameForm(
            {"password1": "unused", "password2": "unused", "email": "test@example.com"}
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {"email": ["Account with this email address already exists."]})

    def test_email_is_more_than_30_chars(self):
        create_user("testuser", email="test@example.com")
        form = AuthUserCreateAccountAutoUsernameForm(
            {"password1": "unused", "password2": "unused", "email": "a.very.long.testuser@example.com"}
        )
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, "a.very.long.testuser@example.c")

    def test_email_makes_username_not_unique(self):
        create_user(username="a.very.long.testuser@example.c", email="a.very.long.testuser@example.co.uk")
        form = AuthUserCreateAccountAutoUsernameForm(
            {"password1": "unused", "password2": "unused", "email": "a.very.long.testuser@example.com"}
        )
        self.assertTrue(form.is_valid())
        with self.assertRaisesRegex(ValidationError, "^.*name already exists.*$"):
            form.save()
