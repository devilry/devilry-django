from django import test
from django.conf import settings
from django.core import mail

from model_mommy import mommy


class TestMessage(test.TestCase):
    def __make_email_for_user(self, user, email):
        return mommy.make('devilry_account.UserEmail', user=user, email=email)

    def test_html_content_cleaning(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        self.__make_email_for_user(testuser, 'testuser@example.com')
        message_receiver = mommy.make('devilry_message.MessageReceiver',
                                      user=testuser,
                                      subject='Test subject',
                                      message_content_html='<p>Test content</p>')
        self.assertEqual(message_receiver.message_content_plain, '')
        message_receiver.full_clean()
        self.assertEqual(message_receiver.message_content_plain, 'Test content')

    def test_send_email_sanity(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        self.__make_email_for_user(testuser, 'testuser@example.com')
        message_receiver = mommy.make('devilry_message.MessageReceiver',
                                      user=testuser,
                                      subject='Test subject',
                                      message_content_html='Test content')
        message_receiver.send()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '[Devilry] Test subject')
        self.assertIn('Test content', mail.outbox[0].message().as_string())
