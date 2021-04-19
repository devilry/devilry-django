import mock

from django import test
from django.conf import settings
from django.core import mail
from django.test import override_settings
from django.utils import timezone

from model_bakery import baker

from devilry.devilry_message.models import MessageReceiver


class TestMessage(test.TestCase):
    def __make_email_for_user(self, user, email):
        return baker.make('devilry_account.UserEmail', user=user, email=email)

    def test_html_content_cleaning(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_email_for_user(testuser, 'testuser@example.com')
        message_receiver = baker.make('devilry_message.MessageReceiver',
                                      user=testuser,
                                      subject='Test subject',
                                      message_content_html='<p>Test content</p>')
        self.assertEqual(message_receiver.message_content_plain, '')
        message_receiver.full_clean()
        self.assertEqual(message_receiver.message_content_plain, 'Test content')

    def test_send_email_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        self.__make_email_for_user(testuser, 'testuser@example.com')
        message_receiver = baker.make('devilry_message.MessageReceiver',
                                      user=testuser,
                                      subject='Test subject',
                                      message_content_html='Test content')
        message_receiver.send()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '[Devilry] Test subject')
        self.assertIn('Test content', mail.outbox[0].message().as_string())

    def __make_simple_message_receiver(self, user, **kwargs):
        return baker.make('devilry_message.MessageReceiver',
                          message_content_html='<p>Test content</p>',
                          message_content_plain='Test content',
                          subject='Test subject',
                          user=user,
                          message_type=['email'], **kwargs)

    def test_status_error(self):
        user = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser@example.com').user
        message_receiver = self.__make_simple_message_receiver(user=user)

        def mock_send_email(instance):
            raise ValueError('Test error')
        with mock.patch('devilry.devilry_message.models.MessageReceiver._send_email', mock_send_email):
            message_receiver.send()
            message_receiver.refresh_from_db()
            self.assertIn('errors', message_receiver.status_data)
            self.assertEqual(len(message_receiver.status_data['errors']), 1)
            self.assertEqual(message_receiver.status_data['errors'][0]['error_message'], 'Test error')

    def test_multiple_status_error_appended(self):
        user = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser@example.com').user
        message_receiver = self.__make_simple_message_receiver(user=user)

        def mock_send_email(instance):
            raise ValueError('Test error')
        with mock.patch('devilry.devilry_message.models.MessageReceiver._send_email', mock_send_email):
            message_receiver.send()
            message_receiver.send()
            message_receiver.send()
            message_receiver.refresh_from_db()
            self.assertIn('errors', message_receiver.status_data)
            self.assertEqual(len(message_receiver.status_data['errors']), 3)
            self.assertEqual(message_receiver.status_data['errors'][0]['error_message'], 'Test error')
            self.assertEqual(message_receiver.status_data['errors'][1]['error_message'], 'Test error')
            self.assertEqual(message_receiver.status_data['errors'][2]['error_message'], 'Test error')

    @override_settings(DEVILRY_MESSAGE_RESEND_LIMIT=3)
    def test_single_send_call_failed_count(self):
        user = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser@example.com').user
        message_receiver = self.__make_simple_message_receiver(user=user)

        def mock_send_email(instance):
            raise ValueError('Test error')
        with mock.patch('devilry.devilry_message.models.MessageReceiver._send_email', mock_send_email):
            message_receiver.send()
            message_receiver.refresh_from_db()
            self.assertEqual(message_receiver.sending_failed_count, 1)

    @override_settings(DEVILRY_MESSAGE_RESEND_LIMIT=3)
    def test_single_send_call_failed_count(self):
        user = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser@example.com').user
        message_receiver = self.__make_simple_message_receiver(user=user)

        def mock_send_email(instance):
            raise ValueError('Test error')

        with mock.patch('devilry.devilry_message.models.MessageReceiver._send_email', mock_send_email):
            message_receiver.send()
            message_receiver.send()
            message_receiver.send()
            message_receiver.refresh_from_db()
            self.assertEqual(message_receiver.sending_failed_count, 3)

    @override_settings(DEVILRY_MESSAGE_RESEND_LIMIT=3)
    def test_send_failed_below_resend_limit(self):
        user = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser@example.com').user
        message_receiver = self.__make_simple_message_receiver(user=user)

        def mock_send_email(instance):
            raise ValueError('Test error')
        with mock.patch('devilry.devilry_message.models.MessageReceiver._send_email', mock_send_email):
            message_receiver.send()
            message_receiver.refresh_from_db()
            self.assertEqual(message_receiver.status, 'failed')

    @override_settings(DEVILRY_MESSAGE_RESEND_LIMIT=3)
    def test_send_failed_equal_to_resend_limit(self):
        user = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser@example.com').user
        message_receiver = self.__make_simple_message_receiver(user=user, sending_failed_count=3)

        def mock_send_email(instance):
            raise ValueError('Test error')

        with mock.patch('devilry.devilry_message.models.MessageReceiver._send_email', mock_send_email):
            message_receiver.send()
            message_receiver.refresh_from_db()
            self.assertEqual(message_receiver.status, 'error')

    @override_settings(DEVILRY_MESSAGE_RESEND_LIMIT=3)
    def test_send_failed_greater_than_resend_limit(self):
        user = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser@example.com').user
        message_receiver = self.__make_simple_message_receiver(user=user, sending_failed_count=4)

        def mock_send_email(instance):
            raise ValueError('Test error')

        with mock.patch('devilry.devilry_message.models.MessageReceiver._send_email', mock_send_email):
            message_receiver.send()
            message_receiver.refresh_from_db()
            self.assertEqual(message_receiver.status, 'error')

    @override_settings(DEVILRY_MESSAGE_RESEND_LIMIT=3)
    def test_single_send_call_success_count(self):
        user = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser@example.com').user
        message_receiver = self.__make_simple_message_receiver(user=user)
        message_receiver.send()
        message_receiver.refresh_from_db()
        self.assertEqual(message_receiver.status, 'sent')
        self.assertEqual(message_receiver.sending_success_count, 1)

    @override_settings(DEVILRY_MESSAGE_RESEND_LIMIT=3)
    def test_multiple_send_call_success_count(self):
        user = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser@example.com').user
        message_receiver = self.__make_simple_message_receiver(user=user)
        message_receiver.send()
        message_receiver.send()
        message_receiver.send()
        message_receiver.refresh_from_db()
        self.assertEqual(message_receiver.status, 'sent')
        self.assertEqual(message_receiver.sending_success_count, 3)

    def test_filter_old_receivers_single_sanity(self):
        created_datetime = timezone.now() - timezone.timedelta(days=10)
        delete_created_before_datetime = timezone.now() - timezone.timedelta(days=5)
        receiver = baker.make('devilry_message.MessageReceiver', created_datetime=created_datetime)
        queryset = MessageReceiver.objects.filter_old_receivers(datetime_obj=delete_created_before_datetime)
        self.assertIn(receiver, queryset)

    def test_filter_old_receivers_multiple_sanity(self):
        created_datetime = timezone.now() - timezone.timedelta(days=10)
        delete_created_before_datetime = timezone.now() - timezone.timedelta(days=5)
        receivers = baker.make('devilry_message.MessageReceiver', created_datetime=created_datetime, _quantity=10)
        queryset = MessageReceiver.objects.filter_old_receivers(datetime_obj=delete_created_before_datetime)
        self.assertEqual(queryset.count(), 10)

    def test_filter_old_receivers_do_not_filter_receivers_created_after_delete_datetime_sanity(self):
        before_delete_created_datetime = timezone.now() - timezone.timedelta(days=10)
        after_delete_created_datetime = timezone.now()
        delete_created_before_datetime = timezone.now() - timezone.timedelta(days=5)

        delete_receivers = baker.make('devilry_message.MessageReceiver',
                                      created_datetime=before_delete_created_datetime, _quantity=10)
        receivers = baker.make('devilry_message.MessageReceiver',
                               created_datetime=after_delete_created_datetime, _quantity=5)

        to_delete_ids = [receiver.id for receiver in delete_receivers]
        not_delete_ids = [receiver.id for receiver in receivers]

        queryset = MessageReceiver.objects.filter_old_receivers(datetime_obj=delete_created_before_datetime)
        self.assertEqual(queryset.count(), 10)

        for receiver in queryset:
            self.assertIn(receiver.id, to_delete_ids)

        for receiver in queryset:
            self.assertNotIn(receiver.id, not_delete_ids)
