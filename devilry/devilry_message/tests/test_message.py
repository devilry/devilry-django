import mock
from django import test
from django.conf import settings
from django.core import mail

from model_bakery import baker

from devilry.devilry_message.models import MessageReceiver, Message
from devilry.devilry_message.tests import test_utils


class TestMessage(test.TestCase):
    def __make_email_for_user(self, user, email):
        return baker.make('devilry_account.UserEmail', user=user, email=email)

    def test_validate_user_ids_not_in_virtual_message_receivers(self):
        message = baker.make('devilry_message.Message', virtual_message_receivers={'test': 'lol'},
                             message_type=['email'])
        with self.assertRaisesMessage(ValueError, 'Missing \'user_ids\' in \'virtual_message_receivers\''):
            message.validate_virtual_message_receivers()

    def test_validate_virtual_message_receivers_not_list(self):
        message = baker.make('devilry_message.Message', virtual_message_receivers={'user_ids': {}},
                             message_type=['email'])
        with self.assertRaisesMessage(ValueError, '\'user_ids\' in \'virtual_message_receivers\' is not a list'):
            message.validate_virtual_message_receivers()

    def test_validate_virtual_message_receivers_empty(self):
        message = baker.make('devilry_message.Message', virtual_message_receivers={'user_ids': []},
                             message_type=['email'])
        with self.assertRaisesMessage(ValueError, '\'user_ids\' in \'virtual_message_receivers\' is empty'):
            message.validate_virtual_message_receivers()

    def test_validate_virtual_message_receivers_contains_non_integer_values(self):
        message = baker.make('devilry_message.Message', virtual_message_receivers={'user_ids': [1, '23']},
                             message_type=['email'])
        with self.assertRaisesMessage(ValueError, '\'virtual_message_receivers["user_ids"]\' contains a non-integer value.: 23'):
            message.validate_virtual_message_receivers()

    def test_prepare_single_message_receiver(self):
        user = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser@example.com').user
        message = baker.make('devilry_message.Message', virtual_message_receivers={'user_ids': [user.id]},
                             message_type=['email'])
        message_receivers = message.prepare_message_receivers(
            subject_generator=test_utils.SubjectTextTestGenerator(),
            template_name='devilry_message/for_test.django.html',
            template_context={})
        self.assertEqual(len(message_receivers), 1)
        self.assertEqual(message_receivers[0].user, user)

    def test_prepare_multiple_message_receivers(self):
        user1 = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser1@example.com').user
        user2 = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser2@example.com').user
        user3 = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser3@example.com').user
        message = baker.make('devilry_message.Message',
                             virtual_message_receivers={'user_ids': [user1.id, user2.id, user3.id]},
                             message_type=['email'])
        message_receivers = message.prepare_message_receivers(
            subject_generator=test_utils.SubjectTextTestGenerator(),
            template_name='devilry_message/for_test.django.html',
            template_context={})
        self.assertEqual(len(message_receivers), 3)
        receiver_user_list = [message_receiver.user for message_receiver in message_receivers]
        self.assertIn(user1, receiver_user_list)
        self.assertIn(user2, receiver_user_list)
        self.assertIn(user3, receiver_user_list)

    def test_prepare_and_send_message_not_draft(self):
        user = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser@example.com').user
        message_preparing = baker.make('devilry_message.Message',
                                       virtual_message_receivers={'user_ids': [user.id]},
                                       message_type=['email'], status='preparing')
        message_sending = baker.make('devilry_message.Message',
                                     virtual_message_receivers={'user_ids': [user.id]},
                                     message_type=['email'], status='sending')
        message_error = baker.make('devilry_message.Message',
                                   virtual_message_receivers={'user_ids': [user.id]},
                                   message_type=['email'], status='error')
        message_sent = baker.make('devilry_message.Message',
                                  virtual_message_receivers={'user_ids': [user.id]},
                                  message_type=['email'], status='sent')
        with self.assertRaisesMessage(ValueError, 'Can only send drafted messages.'):
            message_preparing.prepare_and_send(
                subject_generator=test_utils.SubjectTextTestGenerator(),
                template_name='devilry_message/for_test.django.html',
                template_context={})

        with self.assertRaisesMessage(ValueError, 'Can only send drafted messages.'):
            message_sending.prepare_and_send(
                subject_generator=test_utils.SubjectTextTestGenerator(),
                template_name='devilry_message/for_test.django.html',
                template_context={})

        with self.assertRaisesMessage(ValueError, 'Can only send drafted messages.'):
            message_error.prepare_and_send(
                subject_generator=test_utils.SubjectTextTestGenerator(),
                template_name='devilry_message/for_test.django.html',
                template_context={})

        with self.assertRaisesMessage(ValueError, 'Can only send drafted messages.'):
            message_sent.prepare_and_send(
                subject_generator=test_utils.SubjectTextTestGenerator(),
                template_name='devilry_message/for_test.django.html',
                template_context={})

    def test_prepare_and_send_ok(self):
        user1 = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser1@example.com').user
        user2 = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser2@example.com').user
        message = baker.make('devilry_message.Message',
                             virtual_message_receivers={'user_ids': [user1.id, user2.id]},
                             message_type=['email'])
        message.prepare_and_send(
            subject_generator=test_utils.SubjectTextTestGenerator(),
            template_name='devilry_message/for_test.django.html',
            template_context={})

        self.assertEqual(MessageReceiver.objects.count(), 2)
        self.assertEqual(MessageReceiver.objects.filter(status='sent').count(), 2)
        self.assertTrue(MessageReceiver.objects.filter(user=user1).exists())
        self.assertTrue(MessageReceiver.objects.filter(user=user2).exists())
        self.assertEqual(len(mail.outbox), 2)

    def test_prepare_and_send_create_message_receivers_raises_error(self):
        user = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser@example.com').user
        message = baker.make('devilry_message.Message',
                             virtual_message_receivers={'user_ids': [user.id]},
                             message_type=['email'])

        def mock_create_message_receivers(instance, subject_generator, template_name, template_context):
            raise ValueError('Test error')

        with mock.patch('devilry.devilry_message.models.Message.create_message_receivers',
                        mock_create_message_receivers):
            message.prepare_and_send(
                subject_generator=test_utils.SubjectTextTestGenerator(),
                template_name='devilry_message/for_test.django.html',
                template_context={})
            message.refresh_from_db()

            self.assertEqual(message.status, 'error')

    def test_single_status_error(self):
        user = self.__make_email_for_user(baker.make(settings.AUTH_USER_MODEL), 'testuser@example.com').user
        message = baker.make('devilry_message.Message',
                             virtual_message_receivers={'user_ids': [user.id]},
                             message_type=['email'])

        def mock_create_message_receivers(instance, subject_generator, template_name, template_context):
            raise ValueError('Test error')

        with mock.patch('devilry.devilry_message.models.Message.create_message_receivers',
                        mock_create_message_receivers):
            message.prepare_and_send(
                subject_generator=test_utils.SubjectTextTestGenerator(),
                template_name='devilry_message/for_test.django.html',
                template_context={})
            message.refresh_from_db()

            self.assertEqual(message.status, 'error')
            self.assertEqual(len(message.status_data), 1)
            self.assertEqual(message.status_data['errors'][0]['error_message'], 'Test error')

    def test_prepare_and_send_query_count(self):
        user_ids = []
        for i in range(1, 10):
            user = self.__make_email_for_user(
                baker.make(settings.AUTH_USER_MODEL),
                'testuser{}@example.com'.format(i)
            ).user
            user_ids.append(user.id)
        message = baker.make('devilry_message.Message',
                             virtual_message_receivers={'user_ids': user_ids},
                             message_type=['email'])
        with self.assertNumQueries(44):
            message.prepare_and_send(
                subject_generator=test_utils.SubjectTextTestGenerator(),
                template_name='devilry_message/for_test.django.html',
                template_context={})

    def test_queryset_filter_messages_with_no_message_receivers_sanity(self):
        message1 = baker.make('devilry_message.Message', message_type=['email'])
        queryset = Message.objects.filter_message_with_no_message_receivers()
        self.assertIn(message1, queryset)

    def test_queryset_filter_messages_with_receiver_not_filterd_sanity(self):
        message = baker.make('devilry_message.Message', message_type=['email'])
        baker.make('devilry_message.MessageReceiver', message=message)
        queryset = Message.objects.filter_message_with_no_message_receivers()
        self.assertEqual(queryset.count(), 0)

    def test_queryset_filter_messages_multiple_none_filterd_sanity(self):
        message1 = baker.make('devilry_message.Message', message_type=['email'])
        message2 = baker.make('devilry_message.Message', message_type=['email'])
        baker.make('devilry_message.MessageReceiver', message=message1)
        baker.make('devilry_message.MessageReceiver', message=message2, _quantity=10)
        queryset = Message.objects.filter_message_with_no_message_receivers()
        self.assertEqual(queryset.count(), 0)

    def test_queryset_filter_messages_with_and_without_receivers_exist_sanity(self):
        message_without_receivers = baker.make('devilry_message.Message', message_type=['email'])
        message_with_receivers = baker.make('devilry_message.Message', message_type=['email'])
        baker.make('devilry_message.MessageReceiver', message=message_with_receivers, _quantity=10)
        self.assertEqual(Message.objects.count(), 2)
        queryset = Message.objects.filter_message_with_no_message_receivers()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(message_without_receivers, queryset)
