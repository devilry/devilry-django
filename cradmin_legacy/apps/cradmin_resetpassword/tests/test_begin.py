from django.core import mail
from django.urls import reverse
from django.test import TestCase
import htmls
from cradmin_legacy.python2_compatibility import mock

from django_cradmin.apps.cradmin_generic_token_with_metadata.models import GenericTokenWithMetadata
from cradmin_legacy.apps.cradmin_resetpassword.views.begin import BeginPasswordResetView
from cradmin_legacy.tests.helpers import create_user


class TestBeginPasswordResetView(TestCase):
    def setUp(self):
        self.url = reverse("cradmin-resetpassword-begin")

    def test_get(self):
        response = self.client.get(self.url)
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists("form#cradmin_legacy_resetpassword_begin_form"))
        self.assertEqual(selector.one("h1").alltext_normalized, "Find your account")
        self.assertIn("Type in your email-address", selector.one(".page-header").alltext_normalized)
        self.assertTrue(selector.exists('input[type="email"][name="email"]'))
        self.assertEqual(selector.one('button[type="submit"]').alltext_normalized, "Search")

    def test_post_user_not_found(self):
        response = self.client.post(self.url, {"email": "testuser@example.com"})
        self.assertEqual(response.status_code, 200)
        selector = htmls.S(response.content)
        self.assertIn(
            "No account with this email address found",
            selector.one("form#cradmin_legacy_resetpassword_begin_form").alltext_normalized,
        )

    def test_post_user_found(self):
        create_user("testuser", email="testuser@example.com")
        with mock.patch.object(BeginPasswordResetView, "_generate_token", lambda s, user: "testtoken"):
            with self.settings(CRADMIN_LEGACY_SITENAME="Testsite"):
                response = self.client.post(self.url, {"email": "testuser@example.com"})
        self.assertRedirects(response, reverse("cradmin-resetpassword-email-sent"))

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Reset your Testsite password")
        self.assertIn("http://testserver/cradmin_resetpassword/reset/testtoken", mail.outbox[0].alternatives[0][0])
        self.assertIn(
            "We received a request to reset the password for your Testsite account, testuser",
            mail.outbox[0].alternatives[0][0],
        )

    def test_post_token_created(self):
        create_user("testuser", email="testuser@example.com")
        self.assertEqual(GenericTokenWithMetadata.objects.count(), 0)
        self.client.post(self.url, {"email": "testuser@example.com"})
        self.assertEqual(GenericTokenWithMetadata.objects.count(), 1)
        token = GenericTokenWithMetadata.objects.first()
        self.assertIsNotNone(token.expiration_datetime)
