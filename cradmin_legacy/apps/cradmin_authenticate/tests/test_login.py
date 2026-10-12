from django.test import TestCase
from django.urls import reverse
import htmls
from cradmin_legacy.apps.cradmin_authenticate.tests.cradmin_authenticate_testapp.models import EmailUser
from django.test.utils import override_settings

from cradmin_legacy.tests.views.helpers import create_testuser


class TestUsernameLogin(TestCase):
    def setUp(self):
        self.testuser = create_testuser(username="testuser")
        self.url = reverse("cradmin-authenticate-login")

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEqual(selector.one("h1").alltext_normalized, "Sign in")

    def test_login_ok(self):
        response = self.client.post(self.url, {"username": "testuser", "password": "test"})
        self.assertEqual(response.status_code, 302)

    def test_login_invalid(self):
        response = self.client.post(self.url, {"username": "testuser", "password": "invalid"})
        self.assertEqual(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertIn(
            "Your username and password didn't match",
            selector.one("#cradmin_authenticate_login_form").alltext_normalized,
        )


class TestEmailLogin(TestCase):
    def setUp(self):
        self.testuser = EmailUser(email="testuser@example.com")
        self.testuser.set_password("test")
        self.testuser.save()
        self.url = reverse("cradmin-authenticate-login")

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertEqual(selector.one("h1").alltext_normalized, "Sign in")

    def test_login_ok(self):
        with self.settings(LOGIN_REDIRECT_URL="/login/redirect"):
            response = self.client.post(self.url, {"email": "testuser@example.com", "password": "test"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "/login/redirect")

    def test_login_next(self):
        response = self.client.post(
            f"{self.url}?next=/next", {"email": "testuser@example.com", "password": "test"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "/next")

    def test_login_invalid(self):
        response = self.client.post(self.url, {"email": "testuser@example.com", "password": "invalid"})
        self.assertEqual(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertIn(
            "Your email and password didn't match", selector.one("#cradmin_authenticate_login_form").alltext_normalized
        )


TestEmailLogin = override_settings(
    AUTH_USER_MODEL="cradmin_authenticate_testapp.EmailUser", CRADMIN_LEGACY_USE_EMAIL_AUTH=True
)(TestEmailLogin)
