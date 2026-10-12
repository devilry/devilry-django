from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
import htmls

from django_cradmin.apps.cradmin_generic_token_with_metadata.models import GenericTokenWithMetadata
from cradmin_legacy.tests.helpers import create_user


class TestBeginRegisterAccountView(TestCase):
    def setUp(self):
        self.url = reverse("cradmin-register-account-begin")

    def test_get(self):
        response = self.client.get(self.url)
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists("form#cradmin_legacy_register_account_form"))
        self.assertEqual(selector.one("h1").alltext_normalized, "Create your Testsite account")
        self.assertEqual(selector.one("title").alltext_normalized, "Create your Testsite account")
        self.assertTrue(selector.exists('input[type="email"][name="email"]'))
        self.assertTrue(selector.exists('input[type="text"][name="username"]'))
        self.assertTrue(selector.exists('input[type="password"][name="password1"]'))
        self.assertTrue(selector.exists('input[type="password"][name="password2"]'))
        self.assertEqual(selector.one('button[type="submit"]').alltext_normalized, "Sign up for Testsite")

    def test_post_email_not_unique(self):
        create_user("testuser", email="testuser@example.com")
        response = self.client.post(
            self.url, {"username": "test", "password1": "test", "password2": "test", "email": "testuser@example.com"}
        )
        self.assertEqual(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertIn(
            "Account with this email address already exists",
            selector.one("form#cradmin_legacy_register_account_form").alltext_normalized,
        )

    def test_post_passwords_not_matching(self):
        response = self.client.post(
            self.url, {"username": "test", "password1": "test1", "password2": "test2", "email": "test@example.com"}
        )
        self.assertEqual(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertIn(
            "The passwords do not match", selector.one("form#cradmin_legacy_register_account_form").alltext_normalized
        )

    def test_post_creates_token(self):
        self.assertEqual(GenericTokenWithMetadata.objects.count(), 0)
        self.client.post(
            self.url, {"username": "test", "password1": "test", "password2": "test", "email": "test@example.com"}
        )
        self.assertEqual(GenericTokenWithMetadata.objects.count(), 1)
        token = GenericTokenWithMetadata.objects.first()
        self.assertIsNotNone(token.expiration_datetime)

    def test_post_creates_user(self):
        self.assertEqual(get_user_model().objects.count(), 0)
        self.client.post(
            self.url, {"username": "test", "password1": "test", "password2": "test", "email": "test@example.com"}
        )
        self.assertEqual(get_user_model().objects.count(), 1)
        created_user = get_user_model().objects.first()
        self.assertEqual(created_user.username, "test")
        self.assertEqual(created_user.email, "test@example.com")
        self.assertTrue(created_user.has_usable_password())
        self.assertTrue(created_user.check_password("test"))

    def test_post_next_url_as_querystring_argument(self):
        self.assertEqual(get_user_model().objects.count(), 0)
        self.client.post(
            f"{self.url}?next=/next",
            {"username": "test", "password1": "test", "password2": "test", "email": "test@example.com"},
        )
        token = GenericTokenWithMetadata.objects.first()
        self.assertEqual(token.metadata["next_url"], "/next")

    def test_post_next_url_as_cradmin_legacy_register_account_redirect_url_setting(self):
        self.assertEqual(get_user_model().objects.count(), 0)
        with self.settings(CRADMIN_LEGACY_REGISTER_ACCOUNT_REDIRECT_URL="/redirect"):
            self.client.post(
                self.url, {"username": "test", "password1": "test", "password2": "test", "email": "test@example.com"}
            )
        token = GenericTokenWithMetadata.objects.first()
        self.assertEqual(token.metadata["next_url"], "/redirect")

    def test_post_next_url_as_login_url_setting(self):
        self.assertEqual(get_user_model().objects.count(), 0)
        with self.settings(LOGIN_URL="/login"):
            self.client.post(
                self.url, {"username": "test", "password1": "test", "password2": "test", "email": "test@example.com"}
            )
        token = GenericTokenWithMetadata.objects.first()
        self.assertEqual(token.metadata["next_url"], "/login")
