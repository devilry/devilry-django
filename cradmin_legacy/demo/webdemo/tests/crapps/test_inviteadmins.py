from django.test import TestCase, RequestFactory
from django.core import mail
import htmls
from cradmin_legacy.python2_compatibility import mock
from cradmin_legacy.demo.webdemo.views.inviteadmins.send import SendInvitesView

from cradmin_legacy.demo.webdemo.models import Site
from django_cradmin.apps.cradmin_generic_token_with_metadata.models import GenericTokenWithMetadata


class TestInviteAdmins(TestCase):
    def setUp(self):
        self.testsite = Site.objects.create(name="testsite")
        self.factory = RequestFactory()

    def test_post_invalid_email_no_invite_sent(self):
        request = self.factory.post("/test", {"emails": "invalid"})
        request.cradmin_role = self.testsite
        self.assertEqual(GenericTokenWithMetadata.objects.count(), 0)
        SendInvitesView.as_view()(request)
        self.assertEqual(GenericTokenWithMetadata.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_post_invalid_email_errormessage(self):
        request = self.factory.post("/test", {"emails": "invalid"})
        request.cradmin_role = self.testsite
        response = SendInvitesView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        self.assertIn("Invalid email address: invalid", selector.one("form").alltext_normalized)

    def test_post_no_emails_no_invite_sent(self):
        request = self.factory.post("/test", {"emails": ""})
        request.cradmin_role = self.testsite
        self.assertEqual(GenericTokenWithMetadata.objects.count(), 0)
        SendInvitesView.as_view()(request)
        self.assertEqual(GenericTokenWithMetadata.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_post_no_emails_errormessage(self):
        request = self.factory.post("/test", {"emails": "invalid"})
        request.cradmin_role = self.testsite
        response = SendInvitesView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        self.assertIn("Invalid email address: invalid", selector.one("form").alltext_normalized)

    def test_post_send_invites(self):
        request = self.factory.post("/test", {"emails": "test1@example.com, test2@example.com"})
        request.cradmin_role = self.testsite
        request.cradmin_app = mock.MagicMock()
        self.assertEqual(GenericTokenWithMetadata.objects.count(), 0)
        response = SendInvitesView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(GenericTokenWithMetadata.objects.count(), 2)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ["test1@example.com"])
        self.assertEqual(mail.outbox[1].to, ["test2@example.com"])
