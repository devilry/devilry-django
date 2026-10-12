from datetime import timedelta, datetime

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

from django.test import TestCase, RequestFactory
from django.utils import timezone
import htmls
from cradmin_legacy.python2_compatibility import mock

from django_cradmin.apps.cradmin_generic_token_with_metadata.models import GenericTokenWithMetadata
from cradmin_legacy.apps.cradmin_invite.baseviews.accept import AbstractAcceptInviteView
from cradmin_legacy.tests.helpers import create_user


class AcceptInviteView(AbstractAcceptInviteView):
    def get_appname(self):
        return "testapp"

    def invite_accepted(self, token):
        return HttpResponse("OK")


class TestAbstractAcceptInviteView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # request._messages = mock.MagicMock()

    def __create_token(self, metadata=None, expiration_datetime=None, **kwargs):
        generic_token_with_metadata = GenericTokenWithMetadata(
            created_datetime=timezone.now(),
            expiration_datetime=(expiration_datetime or (timezone.now() + timedelta(days=2))),
            content_object=create_user("invitecontentobject"),
            app="testapp",
            **kwargs,
        )
        generic_token_with_metadata.metadata = metadata or {}
        generic_token_with_metadata.save()
        return generic_token_with_metadata

    def test_get_expired_token(self):
        self.__create_token(token="valid-token", expiration_datetime=datetime(2014, 1, 1))
        request = self.factory.get("/test")
        response = AcceptInviteView.as_view()(request, token="valid-token")
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists("#cradmin_legacy_invite_expired_message"))
        self.assertEqual(
            selector.one("#cradmin_legacy_invite_expired_message").alltext_normalized, "This invite link has expired."
        )

    def test_get_invalid_token(self):
        self.__create_token(token="valid-token")
        request = self.factory.get("/test")
        response = AcceptInviteView.as_view()(request, token="invalid-token")
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists("#cradmin_legacy_invite_invalid_token_message"))
        self.assertEqual(
            selector.one("#cradmin_legacy_invite_invalid_token_message").alltext_normalized,
            "Invalid invite URL. Are you sure you copied the entire URL from the email?",
        )

    def test_get_render(self):
        request = self.factory.get("/test")
        request.user = mock.MagicMock()
        token = self.__create_token()
        response = AcceptInviteView.as_view()(request, token=token.token)
        self.assertEqual(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        self.assertEqual(selector.one("title").alltext_normalized, "Accept invite")
        self.assertEqual(selector.one(".page-header h1").alltext_normalized, "Accept invite")
        self.assertEqual(
            selector.one("#cradmin_legacy_invite_accept_description").alltext_normalized,
            "TODO: Set a description_template for your AbstractAcceptInviteView subclass.",
        )

    def test_get_render_is_authenticated(self):
        request = self.factory.get("/test")
        request.user = create_user("testuser")
        token = self.__create_token()
        with self.settings(CRADMIN_LEGACY_SITENAME="Testsite"):
            response = AcceptInviteView.as_view()(request, token=token.token)
        self.assertEqual(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists("button#cradmin_legacy_invite_accept_as_button"))
        self.assertEqual(
            selector.one("#cradmin_legacy_invite_accept_register_account_button")["href"],
            "/cradmin_register_account/begin?next=http%3A%2F%2Ftestserver%2Ftest",
        )
        self.assertEqual(
            selector.one("#cradmin_legacy_invite_accept_login_as_different_user_button")["href"],
            "/cradmin_authenticate/logout?next=%2Faccounts%2Flogin%2F%3Fnext%3Dhttp%253A%252F%252Ftestserver%252Ftest",
        )

        self.assertEqual(
            selector.one("button#cradmin_legacy_invite_accept_as_button").alltext_normalized, "Accept as testuser"
        )
        self.assertEqual(
            selector.one("#cradmin_legacy_invite_accept_register_account_button").alltext_normalized,
            "Sign up for Testsite",
        )
        self.assertEqual(
            selector.one("#cradmin_legacy_invite_accept_login_as_different_user_button").alltext_normalized,
            "Sign in as another user",
        )

    def test_get_render_not_authenticated(self):
        request = self.factory.get("/test")
        request.user = AnonymousUser()
        token = self.__create_token()
        with self.settings(CRADMIN_LEGACY_SITENAME="Testsite"):
            response = AcceptInviteView.as_view()(request, token=token.token)
        self.assertEqual(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        self.assertEqual(
            selector.one("#cradmin_legacy_invite_accept_login_button")["href"],
            "/accounts/login/?next=http%3A%2F%2Ftestserver%2Ftest",
        )
        self.assertEqual(
            selector.one("#cradmin_legacy_invite_accept_register_account_button")["href"],
            "/cradmin_register_account/begin?next=http%3A%2F%2Ftestserver%2Ftest",
        )

        self.assertEqual(selector.one("#cradmin_legacy_invite_accept_login_button").alltext_normalized, "Sign in")
        self.assertEqual(
            selector.one("#cradmin_legacy_invite_accept_register_account_button").alltext_normalized,
            "Sign up for Testsite",
        )

    def test_post_not_authenticated(self):
        request = self.factory.post("/test")
        request.user = AnonymousUser()
        token = self.__create_token()
        with self.assertRaises(PermissionDenied):
            AcceptInviteView.as_view()(request, token=token.token)

    def test_post_is_authenticated(self):
        request = self.factory.post("/test")
        request.user = create_user("testuser")
        token = self.__create_token()
        response = AcceptInviteView.as_view()(request, token=token.token)
        self.assertEqual(response.content, b"OK")
