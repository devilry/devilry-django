from __future__ import unicode_literals

from io import StringIO

from django import test
from django.conf import settings
from django.core import management
from django.core import mail
from model_bakery import baker

from devilry.devilry_message.models import MessageReceiver


class TestResendFailedMessagesCommand(test.TestCase):
    def __test_standard_output(self, stdout, num_resent=0, exceeded_resend_limit=0,
                               resend_limit=settings.DEVILRY_MESSAGE_RESEND_LIMIT):
        self.assertEqual(
            stdout.getvalue().encode(encoding='UTF-8').decode(),
            '{num_resent} messages were automatically resent.\n'
            '{exceeded_resend_limit} messages has exceeded the retry limit '
            '(current limit: {resend_limit})\n'.format(
                num_resent=num_resent,
                exceeded_resend_limit=exceeded_resend_limit,
                resend_limit=resend_limit
            ))

    def __make_email_for_user(self, user, email):
        return baker.make('devilry_account.UserEmail', user=user, email=email)

    def test_no_messages(self):
        out = StringIO()
        management.call_command('devilry_resend_failed_messages', stdout=out)
        self.__test_standard_output(stdout=out)
        out.close()

    def test_sanity_failed_message_sent_to_user(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_email_for_user(testuser, 'testuser@example.com')
        baker.make('devilry_message.MessageReceiver',
                   user=testuser,
                   status=MessageReceiver.STATUS_CHOICES.FAILED.value)
        out = StringIO()
        management.call_command('devilry_resend_failed_messages', stdout=out)
        self.__test_standard_output(stdout=out, num_resent=1)
        out.close()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['testuser@example.com'])

    def test_sanity_failed_messages_sent_to_multiple_users(self):
        testuser1 = baker.make(settings.AUTH_USER_MODEL)
        testuser2 = baker.make(settings.AUTH_USER_MODEL)
        self.__make_email_for_user(testuser1, 'testuser1@example.com')
        self.__make_email_for_user(testuser2, 'testuser2@example.com')
        receiver1 = baker.make('devilry_message.MessageReceiver',
                   user=testuser1,
                   subject='Test 1',
                   status=MessageReceiver.STATUS_CHOICES.FAILED.value)
        receiver2 = baker.make('devilry_message.MessageReceiver',
                   user=testuser2,
                   subject='Test 2',
                   status=MessageReceiver.STATUS_CHOICES.FAILED.value)
        out = StringIO()
        management.call_command('devilry_resend_failed_messages', stdout=out)
        self.__test_standard_output(stdout=out, num_resent=2)
        out.close()
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].recipients(), ['testuser1@example.com'])
        self.assertEqual(mail.outbox[0].subject, '[Devilry] Test 1')
        self.assertEqual(mail.outbox[1].recipients(), ['testuser2@example.com'])
        self.assertEqual(mail.outbox[1].subject, '[Devilry] Test 2')

        receiver1.refresh_from_db()
        receiver2.refresh_from_db()
        self.assertEqual(receiver1.status, MessageReceiver.STATUS_CHOICES.SENT.value)
        self.assertEqual(receiver2.status, MessageReceiver.STATUS_CHOICES.SENT.value)

    def test_stdout_no_failed_messages(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_email_for_user(testuser, 'testuser@example.com')
        baker.make('devilry_message.MessageReceiver',
                   user=testuser,
                   status=MessageReceiver.STATUS_CHOICES.SENT.value)
        out = StringIO()
        management.call_command('devilry_resend_failed_messages', stdout=out)
        self.__test_standard_output(stdout=out)
        out.close()
        self.assertEqual(len(mail.outbox), 0)

    def test_stdout_failed_message_sent(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_email_for_user(testuser, 'testuser@example.com')
        baker.make('devilry_message.MessageReceiver',
                   user=testuser,
                   status=MessageReceiver.STATUS_CHOICES.FAILED.value)
        out = StringIO()
        management.call_command('devilry_resend_failed_messages', stdout=out)
        self.__test_standard_output(stdout=out, num_resent=1)
        out.close()
        self.assertEqual(len(mail.outbox), 1)

    def test_stdout_multiple_failed_messages_sent(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_email_for_user(testuser, 'testuser@example.com')
        baker.make('devilry_message.MessageReceiver',
                   user=testuser,
                   status=MessageReceiver.STATUS_CHOICES.FAILED.value)
        baker.make('devilry_message.MessageReceiver',
                   user=testuser,
                   status=MessageReceiver.STATUS_CHOICES.FAILED.value)
        out = StringIO()
        management.call_command('devilry_resend_failed_messages', stdout=out)
        self.__test_standard_output(stdout=out, num_resent=2)
        out.close()
        self.assertEqual(len(mail.outbox), 2)

    def test_stdout_failed_message_exceeded_resend_limit(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_email_for_user(testuser, 'testuser@example.com')
        baker.make('devilry_message.MessageReceiver',
                   user=testuser,
                   status=MessageReceiver.STATUS_CHOICES.FAILED.value,
                   sending_failed_count=settings.DEVILRY_MESSAGE_RESEND_LIMIT + 1)
        out = StringIO()
        management.call_command('devilry_resend_failed_messages', stdout=out)
        self.__test_standard_output(stdout=out, exceeded_resend_limit=1)
        out.close()
        self.assertEqual(len(mail.outbox), 0)

    def test_stdout_multiple_failed_messages_exceeded_resend_limit(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_email_for_user(testuser, 'testuser@example.com')
        baker.make('devilry_message.MessageReceiver',
                   user=testuser,
                   status=MessageReceiver.STATUS_CHOICES.FAILED.value,
                   sending_failed_count=settings.DEVILRY_MESSAGE_RESEND_LIMIT + 1)
        baker.make('devilry_message.MessageReceiver',
                   user=testuser,
                   status=MessageReceiver.STATUS_CHOICES.FAILED.value,
                   sending_failed_count=settings.DEVILRY_MESSAGE_RESEND_LIMIT + 1)
        out = StringIO()
        management.call_command('devilry_resend_failed_messages', stdout=out)
        self.__test_standard_output(stdout=out, exceeded_resend_limit=2)
        out.close()
        self.assertEqual(len(mail.outbox), 0)

    def test_stdout_failed_message_and_message_that_exceeded_resend_limit(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_email_for_user(testuser, 'testuser@example.com')
        baker.make('devilry_message.MessageReceiver',
                   user=testuser,
                   status=MessageReceiver.STATUS_CHOICES.FAILED.value)
        baker.make('devilry_message.MessageReceiver',
                   user=testuser,
                   status=MessageReceiver.STATUS_CHOICES.FAILED.value,
                   sending_failed_count=settings.DEVILRY_MESSAGE_RESEND_LIMIT + 1)
        out = StringIO()
        management.call_command('devilry_resend_failed_messages', stdout=out)
        self.__test_standard_output(stdout=out, num_resent=1, exceeded_resend_limit=1)
        out.close()
        self.assertEqual(len(mail.outbox), 1)
