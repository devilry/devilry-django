from django.urls import reverse
from django.test import TestCase
import htmls


class TestEmailSentView(TestCase):
    def setUp(self):
        self.url = reverse("cradmin-resetpassword-email-sent")

    def test_get(self):
        with self.settings(CRADMIN_LEGACY_SITENAME="Testsite"):
            response = self.client.get(self.url)
        selector = htmls.S(response.content)
        self.assertEqual(selector.one("h1").alltext_normalized, "Check your email")
        self.assertIn(
            "We have sent you an email. Click the link in the email to reset your password.",
            selector.one("#cradmin_legacy_focusedlayout_content").alltext_normalized,
        )
        self.assertIn(
            'If you do not see the email, check your junk folder or try searching for "Reset your Testsite password".',
            selector.one("#cradmin_legacy_focusedlayout_content").alltext_normalized,
        )
