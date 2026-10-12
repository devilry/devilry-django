from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, RequestFactory, override_settings
from django.utils import timezone
import htmls
from rest_framework.test import APIRequestFactory

from django_cradmin.apps.cradmin_resetpassword.api.change_password import ChangePasswordApi
from unittest import mock
from django_cradmin.apps.cradmin_resetpassword.views.reset import ResetPasswordView
from django_cradmin.apps.cradmin_generic_token_with_metadata.models import GenericTokenWithMetadata
from django_cradmin.tests.helpers import create_user


class TestResetPasswordView(TestCase):
    apiview_class = ChangePasswordApi

    def setUp(self):
        self.testuser = create_user("testuser")

    def make_request(self, method, viewkwargs=None, api_url="/test/", data=None, requestuser=None):
        factory = APIRequestFactory()
        request = getattr(factory, method)(api_url, format="json", data=data)
        viewkwargs = viewkwargs or {}
        if requestuser:
            request.user = requestuser
        response = self.apiview_class.as_view()(request, **viewkwargs)
        response.render()
        return response

    def make_post_request(self, viewkwargs=None, api_url="/test/", data=None, requestuser=None):
        return self.make_request(
            method="post", viewkwargs=viewkwargs, api_url=api_url, data=data, requestuser=requestuser
        )

    def test_ok_password(self):
        user = self.testuser
        user.set_password("testpassword")
        user.save()

        self.assertTrue(user.check_password("testpassword"))
        response = self.make_post_request(
            requestuser=user, data={"old_password": "testpassword", "new_password": "otherpassword"}
        )
        user.refresh_from_db()
        self.assertTrue(user.check_password("otherpassword"))

    def test_wrong_password(self):
        user = self.testuser
        user.set_password("testpassword")
        user.save()

        self.assertTrue(user.check_password("testpassword"))
        response = self.make_post_request(
            requestuser=user, data={"old_password": "wrong", "new_password": "otherpassword"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"old_password": "Invalid password"})
        user.refresh_from_db()
        self.assertTrue(user.check_password("testpassword"))

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
                "OPTIONS": {
                    "min_length": 10,
                },
            }
        ]
    )
    def test_validate(self):
        user = self.testuser
        user.set_password("testpassword")
        user.save()

        self.assertTrue(user.check_password("testpassword"))
        response = self.make_post_request(
            requestuser=user, data={"old_password": "testpassword", "new_password": "oth"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            str(response.data["password"]), "This password is too short. It must contain at least 10 characters."
        )
