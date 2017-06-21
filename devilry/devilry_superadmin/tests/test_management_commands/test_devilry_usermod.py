from __future__ import unicode_literals

from django import test
from django.core import management
from django.test import override_settings

from devilry.devilry_account.models import User


@override_settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True)
class TestUsermodCommand(test.TestCase):
    def __run_management_command(self, *args):
        management.call_command(
            'devilry_usermod', *args)

    @override_settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False)
    def test_ok_usernames_sanity(self):
        User.objects.create_user(username='test')
        self.__run_management_command('test')

    def test_ok_emails_sanity(self):
        User.objects.create_user(email='test@example.com')
        self.__run_management_command('test@example.com')

    def test_add_email(self):
        user = User.objects.create_user(email='test@example.com')
        self.__run_management_command('test@example.com', '--email=test2@example.com')
        user.refresh_from_db()
        self.assertEqual(user.useremail_set.count(), 2)
        self.assertTrue(user.useremail_set.filter(email='test2@example.com').exists())

    def test_add_existing_email(self):
        user = User.objects.create_user(email='test@example.com')
        self.assertEqual(user.useremail_set.count(), 1)
        self.__run_management_command('test@example.com', '--email=test@example.com')
        user.refresh_from_db()
        self.assertEqual(user.useremail_set.count(), 1)

    def test_set_fullname(self):
        user = User.objects.create_user(email='test@example.com')
        self.assertEqual(user.useremail_set.count(), 1)
        self.__run_management_command('test@example.com', '--full_name=New Full Name')
        user.refresh_from_db()
        self.assertEqual(user.fullname, 'New Full Name')
