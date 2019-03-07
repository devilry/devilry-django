

from django import test
from django.contrib.auth import get_user_model
from django.core import management
from django.test import override_settings


class TestUseraddbulkCommand(test.TestCase):
    def __run_management_command(self, *username_or_email):
        management.call_command(
            'devilry_useraddbulk',
            *username_or_email)

    @override_settings(CRADMIN_LEGACY_USE_EMAIL_AUTH_BACKEND=False)
    def test_ok_usernames_sanity(self):
        self.assertEqual(get_user_model().objects.count(), 0)
        self.__run_management_command('a', 'b', 'c')
        self.assertEqual(get_user_model().objects.count(), 3)

    @override_settings(CRADMIN_LEGACY_USE_EMAIL_AUTH_BACKEND=True)
    def test_ok_emails_sanity(self):
        self.assertEqual(get_user_model().objects.count(), 0)
        self.__run_management_command('a@example.com', 'b@example.com', 'c@example.com')
        self.assertEqual(get_user_model().objects.count(), 3)

    @override_settings(CRADMIN_LEGACY_USE_EMAIL_AUTH_BACKEND=False,
                       DEVILRY_DEFAULT_EMAIL_USERNAME_SUFFIX='example.com')
    def test_ok_usernames_correct_attributes(self):
        self.__run_management_command('a')
        created_user = get_user_model().objects.first()
        self.assertEqual(created_user.shortname, 'a')
        self.assertFalse(created_user.has_usable_password())
        self.assertEqual(created_user.username_set.count(), 1)
        self.assertEqual(created_user.username_set.first().username, 'a')
        self.assertEqual(created_user.useremail_set.count(), 1)
        self.assertEqual(created_user.useremail_set.first().email, 'a@example.com')
        self.assertTrue(created_user.useremail_set.first().use_for_notifications)

    @override_settings(CRADMIN_LEGACY_USE_EMAIL_AUTH_BACKEND=True)
    def test_ok_emails_correct_attributes(self):
        self.__run_management_command('a@test.com')
        created_user = get_user_model().objects.first()
        self.assertEqual(created_user.shortname, 'a@test.com')
        self.assertFalse(created_user.has_usable_password())
        self.assertEqual(created_user.username_set.count(), 0)
        self.assertEqual(created_user.useremail_set.count(), 1)
        self.assertEqual(created_user.useremail_set.first().email, 'a@test.com')
        self.assertTrue(created_user.useremail_set.first().use_for_notifications)
