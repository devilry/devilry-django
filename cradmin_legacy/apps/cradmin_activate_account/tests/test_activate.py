from datetime import timedelta, datetime
from django.contrib import messages

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, RequestFactory
from django.utils import timezone
import htmls
from cradmin_legacy.python2_compatibility import mock
from cradmin_legacy.apps.cradmin_activate_account.views.activate import ActivateAccountView

from django_cradmin.apps.cradmin_generic_token_with_metadata.models import GenericTokenWithMetadata
from cradmin_legacy.tests.helpers import create_user


class TestActivateAccountView(TestCase):
    def setUp(self):
        self.testuser = create_user("testuser", is_active=False)

    def __get_url(self, token):
        return reverse("cradmin-activate-account-activate", kwargs={"token": token})

    def _create_generic_token_with_metadata(
        self, user, created_datetime=None, expiration_datetime=None, metadata=None, **kwargs
    ):
        generic_token_with_metadata = GenericTokenWithMetadata(
            created_datetime=(created_datetime or timezone.now()),
            expiration_datetime=(expiration_datetime or (timezone.now() + timedelta(days=2))),
            app="cradmin_activate_account",
            content_object=user,
            **kwargs,
        )
        if metadata:
            generic_token_with_metadata.metadata = metadata
        generic_token_with_metadata.save()
        return generic_token_with_metadata

    def test_get_expired_token(self):
        self._create_generic_token_with_metadata(
            token="valid-token", user=self.testuser, expiration_datetime=datetime(2014, 1, 1)
        )
        response = self.client.get(self.__get_url("valid-token"))
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists("#cradmin_legacy_activate_account_expired_message"))
        self.assertEqual(
            selector.one("#cradmin_legacy_activate_account_expired_message").alltext_normalized,
            "This account activation link has expired.",
        )

    def test_get_invalid_token(self):
        self._create_generic_token_with_metadata(token="valid-token", user=self.testuser)
        response = self.client.get(self.__get_url("invalid-token"))
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists("#cradmin_legacy_activate_account_invalid_token_message"))
        self.assertEqual(
            selector.one("#cradmin_legacy_activate_account_invalid_token_message").alltext_normalized,
            "Invalid account activation URL. Are you sure you copied the entire URL from the email?",
        )

    def test_get_redirect_ok(self):
        self._create_generic_token_with_metadata(
            token="valid-token", user=self.testuser, metadata={"next_url": "/next"}
        )
        response = self.client.get(self.__get_url("valid-token"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "/next")

    def test_get_activate_ok(self):
        self._create_generic_token_with_metadata(
            token="valid-token", user=self.testuser, metadata={"next_url": "/next"}
        )
        self.assertFalse(self.testuser.is_active)
        self.client.get(self.__get_url("valid-token"))
        testuser = get_user_model().objects.get(id=self.testuser.id)
        self.assertTrue(testuser.is_active)

    def test_post_success_message(self):
        self._create_generic_token_with_metadata(
            token="valid-token", user=self.testuser, metadata={"next_url": "/next"}
        )
        request = RequestFactory().get("/test")
        request.user = self.testuser
        request._messages = mock.MagicMock()
        ActivateAccountView.as_view()(request, token="valid-token")
        request._messages.add.assert_called_once_with(messages.SUCCESS, "Your account is now active.", "")
