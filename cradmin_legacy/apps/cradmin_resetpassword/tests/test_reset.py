from datetime import timedelta, datetime
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, RequestFactory
from django.utils import timezone
import htmls
from cradmin_legacy.python2_compatibility import mock
from cradmin_legacy.apps.cradmin_resetpassword.views.reset import ResetPasswordView
from django_cradmin.apps.cradmin_generic_token_with_metadata.models import GenericTokenWithMetadata
from cradmin_legacy.tests.helpers import create_user


class TestResetPasswordView(TestCase):
    def setUp(self):
        self.testuser = create_user("testuser")

    def __get_url(self, token):
        return reverse("cradmin-resetpassword-reset", kwargs={"token": token})

    def _create_generic_token_with_metadata(self, user, created_datetime=None, expiration_datetime=None, **kwargs):
        generic_token_with_metadata = GenericTokenWithMetadata.objects.create(
            created_datetime=(created_datetime or timezone.now()),
            expiration_datetime=(expiration_datetime or (timezone.now() + timedelta(days=2))),
            content_object=user,
            app="cradmin_resetpassword",
            **kwargs,
        )
        return generic_token_with_metadata

    def test_get(self):
        self._create_generic_token_with_metadata(token="valid-token", user=self.testuser)
        response = self.client.get(self.__get_url("valid-token"))
        selector = htmls.S(response.content)
        self.assertEqual(selector.one("h1").alltext_normalized, "Reset your password testuser")
        self.assertTrue(selector.exists("form#cradmin_legacy_resetpassword_reset_form"))
        self.assertTrue(selector.exists('input[type="password"][name="password1"]'))
        self.assertTrue(selector.exists('input[type="password"][name="password2"]'))

    def test_get_expired_token(self):
        self._create_generic_token_with_metadata(
            token="valid-token", user=self.testuser, expiration_datetime=datetime(2014, 1, 1)
        )
        response = self.client.get(self.__get_url("valid-token"))
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists("form#cradmin_legacy_resetpassword_reset_form"))
        self.assertTrue(selector.exists("#cradmin_legacy_resetpassword_reset_expired_message"))
        self.assertEqual(
            selector.one("#cradmin_legacy_resetpassword_reset_expired_message").alltext_normalized,
            "This password reset link has expired.",
        )

    def test_get_invalid_token(self):
        self._create_generic_token_with_metadata(token="valid-token", user=self.testuser)
        response = self.client.get(self.__get_url("invalid-token"))
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists("form#cradmin_legacy_resetpassword_reset_form"))
        self.assertTrue(selector.exists("#cradmin_legacy_resetpassword_reset_invalid_token_message"))
        self.assertEqual(
            selector.one("#cradmin_legacy_resetpassword_reset_invalid_token_message").alltext_normalized,
            "Invalid password reset URL. Are you sure you copied the entire URL from the email?",
        )

    def test_post_passwords_not_matching(self):
        self._create_generic_token_with_metadata(token="valid-token", user=self.testuser)
        response = self.client.post(
            self.__get_url("valid-token"),
            {
                "password1": "passwordOne",
                "password2": "passwordTwo",
            },
        )
        selector = htmls.S(response.content)
        self.assertIn(
            "The passwords do not match",
            selector.one("form#cradmin_legacy_resetpassword_reset_form").alltext_normalized,
        )

    def test_post_expired_token(self):
        self._create_generic_token_with_metadata(
            token="valid-token", user=self.testuser, expiration_datetime=datetime(2014, 1, 1)
        )
        response = self.client.post(
            self.__get_url("valid-token"),
            {
                "password1": "secret",
                "password2": "secret",
            },
        )
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists("form#cradmin_legacy_resetpassword_reset_form"))
        self.assertTrue(selector.exists("#cradmin_legacy_resetpassword_reset_expired_message"))
        self.assertEqual(
            selector.one("#cradmin_legacy_resetpassword_reset_expired_message").alltext_normalized,
            "This password reset link has expired.",
        )

    def test_post_invalid_token(self):
        self._create_generic_token_with_metadata(token="valid-token", user=self.testuser)
        response = self.client.post(
            self.__get_url("invalid-token"),
            {
                "password1": "secret",
                "password2": "secret",
            },
        )
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists("form#cradmin_legacy_resetpassword_reset_form"))
        self.assertTrue(selector.exists("#cradmin_legacy_resetpassword_reset_invalid_token_message"))
        self.assertEqual(
            selector.one("#cradmin_legacy_resetpassword_reset_invalid_token_message").alltext_normalized,
            "Invalid password reset URL. Are you sure you copied the entire URL from the email?",
        )

    def test_post(self):
        self._create_generic_token_with_metadata(token="valid-token", user=self.testuser)

        with self.settings(CRADMIN_LEGACY_RESETPASSWORD_FINISHED_REDIRECT_URL="http://example.com"):
            response = self.client.post(
                self.__get_url("valid-token"),
                {
                    "password1": "newpassword",
                    "password2": "newpassword",
                },
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://example.com")
        testuser = get_user_model().objects.get(pk=self.testuser.pk)
        self.assertTrue(testuser.check_password("newpassword"))

    def test_post_success_message(self):
        self._create_generic_token_with_metadata(token="valid-token", user=self.testuser)

        request = RequestFactory().post(
            "/test",
            {
                "password1": "newpassword",
                "password2": "newpassword",
            },
        )
        request.user = self.testuser
        request._messages = mock.MagicMock()

        with self.settings(CRADMIN_LEGACY_RESETPASSWORD_FINISHED_REDIRECT_URL="http://example.com"):
            ResetPasswordView.as_view()(request, token="valid-token")
        request._messages.add.assert_called_once_with(messages.SUCCESS, "Your password has been updated.", "")
