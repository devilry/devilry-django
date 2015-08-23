from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy
from devilry.devilry_account.models import User


class TestUser(TestCase):
    def test_get_full_name(self):
        user = mommy.make('devilry_account.User', fullname="Elvis Aron Presley")
        self.assertEqual("Elvis Aron Presley", user.get_full_name())

    def test_get_full_name_fallback_to_shortname(self):
        user = mommy.make('devilry_account.User', shortname='test@example.com')
        self.assertEqual("test@example.com", user.get_full_name())

    def test_is_active(self):
        user = mommy.make('devilry_account.User')
        self.assertTrue(user.is_active)

    def test_is_not_active(self):
        user = mommy.make('devilry_account.User',
                          suspended_datetime=timezone.now())
        self.assertFalse(user.is_active)

    def test_clean_suspended_reason_with_blank_suspended_datetime(self):
        user = mommy.make('devilry_account.User',
                          suspended_datetime=None,
                          suspended_reason='Test')
        with self.assertRaisesMessage(ValidationError,
                                      'Can not provide a reason for suspension when suspension time is blank.'):
            user.clean()

    def test_clean_suspended_reason_with_suspended_datetime(self):
        user = mommy.make('devilry_account.User',
                          suspended_datetime=timezone.now(),
                          suspended_reason='Test')
        user.clean()

    def test_clean_set_lastname_from_fullname(self):
        user = mommy.make('devilry_account.User')
        user.fullname = 'The Test User'
        user.clean()
        self.assertEqual(user.lastname, 'User')

    def test_clean_unset_lastname_when_no_fullname(self):
        user = mommy.make('devilry_account.User',
                          fullname='The Test User')
        user.fullname = ''
        user.clean()
        self.assertEqual(user.lastname, '')


class TestUserManager(TestCase):
    def test_create_user_username(self):
        user = User.objects.create_user(username='testuser')
        self.assertEqual(user.shortname, 'testuser')
        self.assertEqual(user.username_set.count(), 1)
        self.assertEqual(user.username_set.first().username, 'testuser')
        self.assertEqual(user.useremail_set.count(), 0)

    def test_create_user_email(self):
        user = User.objects.create_user(email='testuser@example.com')
        self.assertEqual(user.shortname, 'testuser@example.com')
        self.assertEqual(user.username_set.count(), 0)
        self.assertEqual(user.useremail_set.count(), 1)
        self.assertEqual(user.useremail_set.first().email, 'testuser@example.com')

    def test_create_user_username_or_email_required(self):
        with self.assertRaises(ValidationError):
            User.objects.create_user()

    def test_create_user_no_password(self):
        user = User.objects.create_user(email='testuser@example.com')
        self.assertFalse(user.has_usable_password())

    def test_create_user_password(self):
        user = User.objects.create_user(email='testuser@example.com', password='test')
        self.assertTrue(user.has_usable_password())

    def test_create_user_fullname(self):
        user = User.objects.create_user(email='testuser@example.com',
                                        fullname='The Test User')
        self.assertEqual(user.fullname, 'The Test User')

    def test_create_user_set_lastname_from_fullname(self):
        user = User.objects.create_user(email='testuser@example.com',
                                        fullname='The Test User')
        self.assertEqual(user.lastname, 'User')

    def test_create_user_unset_lastname_when_no_fullname(self):
        user = User.objects.create_user(email='testuser@example.com',
                                        fullname='')
        self.assertEqual(user.lastname, '')


class TestUserEmail(TestCase):
    def test_email_unique(self):
        mommy.make('devilry_account.UserEmail', email='test@example.com')
        with self.assertRaises(IntegrityError):
            mommy.make('devilry_account.UserEmail', email='test@example.com')


class TestUserName(TestCase):
    def test_username_unique(self):
        mommy.make('devilry_account.UserName', username='test')
        with self.assertRaises(IntegrityError):
            mommy.make('devilry_account.UserName', username='test')

    def test_is_primary_unique(self):
        user = mommy.make('devilry_account.User')
        mommy.make('devilry_account.UserName', user=user, is_primary=True)
        with self.assertRaises(IntegrityError):
            mommy.make('devilry_account.UserName', user=user, is_primary=True)

    def test_is_primary_not_unique_for_none(self):
        user = mommy.make('devilry_account.User')
        mommy.make('devilry_account.UserName', user=user, is_primary=None)
        mommy.make('devilry_account.UserName', user=user, is_primary=None)
