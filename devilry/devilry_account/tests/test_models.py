from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from devilry.devilry_account.exceptions import IllegalOperationError
from devilry.devilry_account.models import User, UserEmail, UserName, PermissionGroup, SubjectPermissionGroup, \
    PeriodPermissionGroup


class TestUser(TestCase):
    def test_get_full_name(self):
        user = mommy.make('devilry_account.User', fullname="Elvis Aron Presley")
        self.assertEqual("Elvis Aron Presley", user.get_full_name())

    def test_get_full_name_fallback_to_shortname(self):
        user = mommy.make('devilry_account.User', shortname='test@example.com')
        self.assertEqual("test@example.com", user.get_full_name())

    def test_get_displayname_has_fullname(self):
        user = mommy.make('devilry_account.User', shortname='elvis',
                          fullname="Elvis Aron Presley")
        self.assertEqual("Elvis Aron Presley (elvis)", user.get_displayname())

    def test_get_displayname_fullname_blank(self):
        user = mommy.make('devilry_account.User', shortname='elvis')
        self.assertEqual("elvis", user.get_displayname())

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


class TestUserQuerySet(TestCase):
    def test_prefetch_related_notification_emails(self):
        user = mommy.make('devilry_account.User')
        notification_useremail1 = mommy.make('devilry_account.UserEmail',
                                             user=user,
                                             use_for_notifications=True,
                                             email='test1@example.com')
        notification_useremail2 = mommy.make('devilry_account.UserEmail',
                                             user=user,
                                             use_for_notifications=True,
                                             email='test2@example.com')
        mommy.make('devilry_account.UserEmail',
                   user=user,
                   use_for_notifications=False,
                   email='unused@example.com')
        with self.assertNumQueries(2):
            user_with_prefetch = User.objects \
                .prefetch_related_notification_emails().first()
            self.assertEqual(len(user_with_prefetch.notification_useremail_objects), 2)
            self.assertTrue(isinstance(user_with_prefetch.notification_useremail_objects,
                                       list))
            self.assertEqual({notification_useremail1, notification_useremail2},
                             set(user_with_prefetch.notification_useremail_objects))
            self.assertEqual({'test1@example.com', 'test2@example.com'},
                             set(user_with_prefetch.notification_emails))

    def test_prefetch_related_primary_email(self):
        user = mommy.make('devilry_account.User')
        primary_useremail = mommy.make('devilry_account.UserEmail',
                                       user=user,
                                       email='test@example.com',
                                       is_primary=True)
        mommy.make('devilry_account.UserEmail',
                   user=user,
                   is_primary=None)
        mommy.make('devilry_account.UserEmail',
                   user=user,
                   is_primary=None)
        with self.assertNumQueries(2):
            user_with_prefetch = User.objects \
                .prefetch_related_primary_email().first()
            self.assertEqual(len(user_with_prefetch.primary_useremail_objects), 1)
            self.assertTrue(isinstance(user_with_prefetch.primary_useremail_objects, list))
            self.assertEqual(primary_useremail,
                             user_with_prefetch.primary_useremail_objects[0])
            self.assertEqual(primary_useremail,
                             user_with_prefetch.primary_useremail_object)
            self.assertEqual('test@example.com',
                             user_with_prefetch.primary_email)

    def test_prefetch_related_primary_username(self):
        user = mommy.make('devilry_account.User')
        primary_username = mommy.make('devilry_account.UserName',
                                      user=user,
                                      username='testuser',
                                      is_primary=True)
        mommy.make('devilry_account.UserEmail',
                   user=user,
                   is_primary=None)
        mommy.make('devilry_account.UserEmail',
                   user=user,
                   is_primary=None)
        with self.assertNumQueries(2):
            user_with_prefetch = User.objects \
                .prefetch_related_primary_username().first()
            self.assertEqual(len(user_with_prefetch.primary_username_objects), 1)
            self.assertTrue(isinstance(user_with_prefetch.primary_username_objects, list))
            self.assertEqual(primary_username,
                             user_with_prefetch.primary_username_objects[0])
            self.assertEqual(primary_username,
                             user_with_prefetch.primary_username_object)
            self.assertEqual('testuser',
                             user_with_prefetch.primary_username)

    def test_filter_by_emails(self):
        user1 = mommy.make('devilry_account.User')
        user2 = mommy.make('devilry_account.User')
        user3 = mommy.make('devilry_account.User')
        ignoreduser = mommy.make('devilry_account.User')
        mommy.make('devilry_account.UserEmail', user=user1, email='user1@example.com')
        mommy.make('devilry_account.UserEmail', user=user2, email='user2@example.com')
        mommy.make('devilry_account.UserEmail', user=user3, email='user3@example.com')
        mommy.make('devilry_account.UserEmail', user=ignoreduser, email='ignoreduser@example.com')
        self.assertEqual(
            {user1, user2, user3},
            set(User.objects.filter_by_emails(['user1@example.com', 'user2@example.com', 'user3@example.com']))
        )

    def test_filter_by_usernames(self):
        user1 = mommy.make('devilry_account.User')
        user2 = mommy.make('devilry_account.User')
        user3 = mommy.make('devilry_account.User')
        ignoreduser = mommy.make('devilry_account.User')
        mommy.make('devilry_account.UserName', user=user1, username='user1')
        mommy.make('devilry_account.UserName', user=user2, username='user2')
        mommy.make('devilry_account.UserName', user=user3, username='user3')
        mommy.make('devilry_account.UserName', user=ignoreduser, username='ignoreduser')
        self.assertEqual(
            {user1, user2, user3},
            set(User.objects.filter_by_usernames(['user1', 'user2', 'user3']))
        )


class TestUserManager(TestCase):
    def test_create_user_username(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            user = User.objects.create_user(username='testuser')
            self.assertEqual(user.shortname, 'testuser')
            self.assertEqual(user.username_set.count(), 1)
            self.assertEqual(user.username_set.first().username, 'testuser')
            self.assertEqual(user.useremail_set.count(), 0)

    def test_create_user_username_fails_with_email_auth_backend(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            with self.assertRaises(IllegalOperationError):
                User.objects.create_user(username='testuser')

    def test_create_user_email(self):
        user = User.objects.create_user(email='testuser@example.com')
        self.assertEqual(user.shortname, 'testuser@example.com')
        self.assertEqual(user.username_set.count(), 0)
        self.assertEqual(user.useremail_set.count(), 1)
        self.assertEqual(user.useremail_set.first().email, 'testuser@example.com')
        self.assertTrue(user.useremail_set.first().use_for_notifications)

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

    def test_get_by_email(self):
        user = mommy.make('devilry_account.User')
        mommy.make('devilry_account.UserEmail', user=user, email='test@example.com')
        self.assertEqual(
            User.objects.get_by_email(email='test@example.com'),
            user)

    def test_get_by_email_doesnotexist(self):
        user = mommy.make('devilry_account.User')
        mommy.make('devilry_account.UserEmail', user=user, email='test2@example.com')
        with self.assertRaises(User.DoesNotExist):
            User.objects.get_by_email(email='test@example.com')

    def test_get_by_username(self):
        user = mommy.make('devilry_account.User')
        mommy.make('devilry_account.UserName', user=user, username='test@example.com')
        self.assertEqual(
            User.objects.get_by_username(username='test@example.com'),
            user)

    def test_get_by_username_doesnotexist(self):
        user = mommy.make('devilry_account.User')
        mommy.make('devilry_account.UserName', user=user, username='test2@example.com')
        with self.assertRaises(User.DoesNotExist):
            User.objects.get_by_username(username='test@example.com')

    def test_bulk_create_from_usernames_not_allowed_with_email_auth_backend(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            with self.assertRaises(IllegalOperationError):
                User.objects.bulk_create_from_usernames([])

    def test_bulk_create_from_usernames_empty_input_list(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            created_users, existing_usernames = User.objects.bulk_create_from_usernames([])
            self.assertEqual(created_users.count(), 0)
            self.assertEqual(User.objects.count(), 0)
            self.assertEqual(UserName.objects.count(), 0)
            self.assertEqual(set(), existing_usernames)

    def test_bulk_create_from_usernames_single_new_user(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            created_users, existing_usernames = User.objects.bulk_create_from_usernames(['testuser'])

            self.assertEqual(created_users.count(), 1)
            self.assertEqual(User.objects.count(), 1)
            created_user = created_users.first()
            self.assertEqual(created_user.shortname, 'testuser')
            self.assertFalse(created_user.has_usable_password())

            self.assertEqual(UserName.objects.count(), 1)
            created_username_object = UserName.objects.first()
            self.assertEqual(created_username_object.username, 'testuser')
            self.assertTrue(created_username_object.is_primary)

            self.assertEqual(set(), existing_usernames)

    def test_bulk_create_from_usernames_create_no_useremail_if_default_email_suffix_is_not_defined(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False,
                           DEVILRY_DEFAULT_EMAIL_SUFFIX=''):
            User.objects.bulk_create_from_usernames(['testuser'])
            self.assertEqual(UserEmail.objects.count(), 0)

    def test_bulk_create_from_usernames_create_useremail_if_a_default_email_suffix_is_defined(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False,
                           DEVILRY_DEFAULT_EMAIL_SUFFIX='@example.com'):
            User.objects.bulk_create_from_usernames(['testuser'])
            self.assertEqual(UserEmail.objects.count(), 1)
            created_useremail_object = UserEmail.objects.first()
            self.assertEqual(created_useremail_object.email, 'testuser@example.com')
            self.assertTrue(created_useremail_object.is_primary)
            self.assertTrue(created_useremail_object.use_for_notifications)

    def test_bulk_create_from_usernames_multiple_new_users(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            created_users, existing_usernames = User.objects.bulk_create_from_usernames(
                ['testuser1', 'testuser2', 'testuser3'])

            self.assertEqual(created_users.count(), 3)
            self.assertEqual(User.objects.count(), 3)
            self.assertEqual({'testuser1', 'testuser2', 'testuser3'},
                             set(User.objects.all().values_list('shortname', flat=True)))

            self.assertEqual(UserName.objects.count(), 3)
            self.assertEqual({'testuser1', 'testuser2', 'testuser3'},
                             set(UserName.objects.all().values_list('username', flat=True)))
            self.assertEqual(3, UserName.objects.filter(is_primary=True).count())

            self.assertEqual(set(), existing_usernames)

    def test_bulk_create_from_usernames_exclude_existing(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            mommy.make('devilry_account.User', shortname='testuser1')
            mommy.make('devilry_account.UserName', username='testuser2')

            created_users, existing_usernames = User.objects.bulk_create_from_usernames(
                ['testuser1', 'testuser2', 'testuser3'])

            self.assertEqual(User.objects.count(), 3)
            self.assertEqual(created_users.count(), 1)
            self.assertEqual(created_users.first().shortname, 'testuser3')

            # We only have 2, since ``testuser1`` did not have a UserName
            self.assertEqual(UserName.objects.count(), 2)
            self.assertEqual(created_users.first().username_set.first().username, 'testuser3')

            self.assertEqual({'testuser1', 'testuser2'}, existing_usernames)

    def test_bulk_create_from_emails_not_allowed_with_username_auth_backend(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            with self.assertRaises(IllegalOperationError):
                User.objects.bulk_create_from_emails([])

    def test_bulk_create_from_emails_empty_input_list(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            created_users, existing_emails = User.objects.bulk_create_from_emails([])
            self.assertEqual(created_users.count(), 0)
            self.assertEqual(User.objects.count(), 0)
            self.assertEqual(UserEmail.objects.count(), 0)
            self.assertEqual(set(), existing_emails)

    def test_bulk_create_from_emails_single_new_user(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            created_users, existing_emails = User.objects.bulk_create_from_emails(
                ['testuser@example.com'])

            self.assertEqual(created_users.count(), 1)
            self.assertEqual(User.objects.count(), 1)
            created_user = created_users.first()
            self.assertEqual(created_user.shortname, 'testuser@example.com')
            self.assertFalse(created_user.has_usable_password())

            self.assertEqual(UserEmail.objects.count(), 1)
            created_useremail_object = UserEmail.objects.first()
            self.assertEqual(created_useremail_object.email, 'testuser@example.com')
            self.assertTrue(created_useremail_object.is_primary)
            self.assertTrue(created_useremail_object.use_for_notifications)

            self.assertEqual(UserName.objects.count(), 0)
            self.assertEqual(set(), existing_emails)

    def test_bulk_create_from_emails_multiple_new_users(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            created_users, existing_emails = User.objects.bulk_create_from_emails(
                ['testuser1@example.com', 'testuser2@example.com', 'testuser3@example.com'])

            self.assertEqual(created_users.count(), 3)
            self.assertEqual(User.objects.count(), 3)
            self.assertEqual({'testuser1@example.com', 'testuser2@example.com', 'testuser3@example.com'},
                             set(User.objects.all().values_list('shortname', flat=True)))

            self.assertEqual(UserEmail.objects.count(), 3)
            self.assertEqual({'testuser1@example.com', 'testuser2@example.com', 'testuser3@example.com'},
                             set(UserEmail.objects.all().values_list('email', flat=True)))
            self.assertEqual(3, UserEmail.objects.filter(is_primary=True).count())

            self.assertEqual(set(), existing_emails)

    def test_bulk_create_from_emails_exclude_existing(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            mommy.make('devilry_account.User', shortname='testuser1@example.com')
            mommy.make('devilry_account.UserEmail', email='testuser2@example.com')

            created_users, existing_emails = User.objects.bulk_create_from_emails(
                ['testuser1@example.com', 'testuser2@example.com', 'testuser3@example.com'])

            self.assertEqual(User.objects.count(), 3)
            self.assertEqual(created_users.count(), 1)
            self.assertEqual(created_users.first().shortname, 'testuser3@example.com')

            # We only have 2, since ``testuser1@example.com`` did not have a UserEmail
            self.assertEqual(UserEmail.objects.count(), 2)
            self.assertEqual(created_users.first().useremail_set.first().email, 'testuser3@example.com')

            self.assertEqual({'testuser1@example.com', 'testuser2@example.com'}, existing_emails)


class TestUserEmail(TestCase):
    def test_email_unique(self):
        mommy.make('devilry_account.UserEmail', email='test@example.com')
        with self.assertRaises(IntegrityError):
            mommy.make('devilry_account.UserEmail', email='test@example.com')

    def test_clean_is_primary_can_not_be_false(self):
        useremail = mommy.make('devilry_account.UserEmail')
        useremail.clean()  # No error
        useremail.is_primary = False
        with self.assertRaisesMessage(ValidationError,
                                      'is_primary can not be False. Valid values are: True, None.'):
            useremail.clean()

    def test_clean_useremail_set_is_primary_unsets_other(self):
        user = mommy.make('devilry_account.User')
        useremail1 = mommy.make('devilry_account.UserEmail',
                                user=user,
                                is_primary=True)
        useremail2 = mommy.make('devilry_account.UserEmail',
                                user=user,
                                is_primary=None)
        useremail2.is_primary = True
        useremail2.clean()
        self.assertIsNone(UserEmail.objects.get(pk=useremail1.pk).is_primary)

    def test_clean_set_shortname_if_is_primary(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            user = mommy.make('devilry_account.User', shortname='oldname@example.com')
            emailobject = mommy.make('devilry_account.UserEmail',
                                     email='newname@example.com',
                                     user=user,
                                     is_primary=None)
            emailobject.is_primary = True
            emailobject.clean()
            self.assertEqual(emailobject.email, 'newname@example.com')
            user = User.objects.get(id=user.id)
            self.assertEqual(user.shortname, 'newname@example.com')

    def test_clean_do_not_set_shortname_if_not_primary(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            user = mommy.make('devilry_account.User', shortname='oldname@example.com')
            emailobject = mommy.make('devilry_account.UserEmail',
                                     email='newname@example.com',
                                     user=user,
                                     is_primary=None)
            emailobject.clean()
            self.assertEqual(emailobject.email, 'newname@example.com')
            user = User.objects.get(id=user.id)
            self.assertEqual(user.shortname, 'oldname@example.com')

    def test_clean_set_shortname_if_is_primary_but_not_using_email_auth_backend(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            user = mommy.make('devilry_account.User', shortname='oldname')
            emailobject = mommy.make('devilry_account.UserEmail',
                                     email='newname@example.com',
                                     user=user,
                                     is_primary=None)
            emailobject.is_primary = True
            emailobject.clean()
            self.assertEqual(emailobject.email, 'newname@example.com')
            user = User.objects.get(id=user.id)
            self.assertEqual(user.shortname, 'oldname')


class TestUserName(TestCase):
    def test_username_unique(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            mommy.make('devilry_account.UserName', username='test')
            with self.assertRaises(IntegrityError):
                mommy.make('devilry_account.UserName', username='test')

    def test_is_primary_unique(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            user = mommy.make('devilry_account.User')
            mommy.make('devilry_account.UserName', user=user, is_primary=True)
            with self.assertRaises(IntegrityError):
                mommy.make('devilry_account.UserName', user=user, is_primary=True)

    def test_is_primary_not_unique_for_none(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            user = mommy.make('devilry_account.User')
            mommy.make('devilry_account.UserName', user=user, is_primary=None)
            mommy.make('devilry_account.UserName', user=user, is_primary=None)

    def test_clean_validationerror_if_using_email_backend(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            usernameobject = mommy.make('devilry_account.UserName')
            with self.assertRaisesMessage(ValidationError,
                                          'Can not create UserName objects when the '
                                          'DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND is True.'):
                usernameobject.clean()

    def test_clean_is_primary_can_not_be_false(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            usernameobject = mommy.make('devilry_account.UserName')
            usernameobject.clean()  # No error
            usernameobject.is_primary = False
            with self.assertRaisesMessage(ValidationError,
                                          'is_primary can not be False. Valid values are: True, None.'):
                usernameobject.clean()

    def test_clean_set_is_primary_unsets_other(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            user = mommy.make('devilry_account.User')
            usernameobject1 = mommy.make('devilry_account.UserName',
                                         user=user,
                                         is_primary=True)
            usernameobject2 = mommy.make('devilry_account.UserName',
                                         user=user,
                                         is_primary=None)
            usernameobject2.is_primary = True
            usernameobject2.clean()
            self.assertIsNone(UserName.objects.get(pk=usernameobject1.pk).is_primary)

    def test_clean_set_shortname_if_is_primary(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            user = mommy.make('devilry_account.User', shortname='oldname')
            usernameobject = mommy.make('devilry_account.UserName',
                                        username='newname',
                                        user=user,
                                        is_primary=None)
            usernameobject.is_primary = True
            usernameobject.clean()
            self.assertEqual(usernameobject.username, 'newname')
            user = User.objects.get(id=user.id)
            self.assertEqual(user.shortname, 'newname')

    def test_clean_do_not_set_shortname_if_not_primary(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            user = mommy.make('devilry_account.User', shortname='oldname')
            usernameobject = mommy.make('devilry_account.UserName',
                                        username='newname',
                                        user=user,
                                        is_primary=None)
            usernameobject.clean()
            self.assertEqual(usernameobject.username, 'newname')
            user = User.objects.get(id=user.id)
            self.assertEqual(user.shortname, 'oldname')


class TestPermissionGroup(TestCase):
    def test_grouptype_departmentadmin_can_not_be_editable(self):
        permissiongroup = mommy.prepare('devilry_account.PermissionGroup',
                                        is_custom_manageable=True,
                                        grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
        with self.assertRaisesMessage(ValidationError, 'Department administrator groups '
                                                       'can not be custom manageable.'):
            permissiongroup.clean()

    def test_grouptype_periodadmin_can_be_editable(self):
        permissiongroup = mommy.prepare('devilry_account.PermissionGroup',
                                        is_custom_manageable=True,
                                        grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN)
        permissiongroup.clean()  # No ValidationError

    def test_grouptype_subjectadmin_can_be_editable(self):
        permissiongroup = mommy.prepare('devilry_account.PermissionGroup',
                                        is_custom_manageable=True,
                                        grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        permissiongroup.clean()  # No ValidationError

    def test_grouptype_can_not_be_changed_for_existing_group(self):
        permissiongroup = mommy.make('devilry_account.PermissionGroup',
                                     grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        permissiongroup.grouptype = PermissionGroup.GROUPTYPE_PERIODADMIN
        with self.assertRaisesMessage(ValidationError, 'Permission group type can not'
                                                       ' be changed.'):
            permissiongroup.clean()


class TestPeriodPermissionGroupQuerySet(TestCase):
    def test_user_is_periodadmin_for_period_false_not_in_any_periodpermissiongroup(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        self.assertFalse(PeriodPermissionGroup.objects.user_is_periodadmin_for_period(
            period=testperiod, user=testuser))

    def test_user_is_periodadmin_for_period_true_for_periodadmin(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=mommy.make('devilry_account.PeriodPermissionGroup',
                                              period=testperiod).permissiongroup)
        self.assertTrue(PeriodPermissionGroup.objects.user_is_periodadmin_for_period(
            period=testperiod, user=testuser))

    def test_get_devilryrole_for_user_on_period_not_in_any_permissiongroup(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        self.assertEqual(
            None,
            PeriodPermissionGroup.objects.get_devilryrole_for_user_on_period(
                period=testperiod, user=testuser))

    def test_get_devilryrole_for_user_on_period_superuser(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        self.assertEqual(
            'departmentadmin',
            PeriodPermissionGroup.objects.get_devilryrole_for_user_on_period(
                period=testperiod, user=testuser))

    def test_get_devilryrole_for_user_on_period_departmentadmin(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=mommy.make('devilry_account.SubjectPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN,
                                              subject=testperiod.subject).permissiongroup)
        self.assertEqual(
            'departmentadmin',
            PeriodPermissionGroup.objects.get_devilryrole_for_user_on_period(
                period=testperiod, user=testuser))

    def test_get_devilryrole_for_user_on_period_subjectadmin(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=mommy.make('devilry_account.SubjectPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                              subject=testperiod.subject).permissiongroup)
        self.assertEqual(
            'subjectadmin',
            PeriodPermissionGroup.objects.get_devilryrole_for_user_on_period(
                period=testperiod, user=testuser))

    def test_get_devilryrole_for_user_on_period_periodadmin(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=mommy.make('devilry_account.PeriodPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                              period=testperiod).permissiongroup)
        self.assertEqual(
            'periodadmin',
            PeriodPermissionGroup.objects.get_devilryrole_for_user_on_period(
                period=testperiod, user=testuser))

    def test_get_custom_managable_periodpermissiongroup_for_period_only_custom_managable(self):
        testperiod = mommy.make('core.Period')
        mommy.make('devilry_account.PeriodPermissionGroup',
                   permissiongroup__is_custom_manageable=False,
                   period=testperiod)
        with self.assertRaises(PeriodPermissionGroup.DoesNotExist):
            PeriodPermissionGroup.objects.get_custom_managable_periodpermissiongroup_for_period(
                    period=testperiod)

    def test_get_custom_managable_periodpermissiongroup_for_period_only_in_period(self):
        testperiod = mommy.make('core.Period')
        mommy.make('devilry_account.PeriodPermissionGroup',
                   permissiongroup__is_custom_manageable=True)
        with self.assertRaises(PeriodPermissionGroup.DoesNotExist):
            PeriodPermissionGroup.objects.get_custom_managable_periodpermissiongroup_for_period(
                    period=testperiod)

    def test_get_custom_managable_periodpermissiongroup_for_period(self):
        testperiod = mommy.make('core.Period')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           permissiongroup__is_custom_manageable=True,
                                           period=testperiod)
        self.assertEqual(
            periodpermissiongroup,
            PeriodPermissionGroup.objects.get_custom_managable_periodpermissiongroup_for_period(
                    period=testperiod))

    def test_get_custom_managable_periodpermissiongroup_for_period_selectrelated_permissiongroup(self):
        testperiod = mommy.make('core.Period')
        mommy.make('devilry_account.PeriodPermissionGroup',
                   permissiongroup__is_custom_manageable=True,
                   period=testperiod)
        periodpermissiongroup = PeriodPermissionGroup.objects.get_custom_managable_periodpermissiongroup_for_period(
            period=testperiod)
        with self.assertNumQueries(0):
            str(periodpermissiongroup.permissiongroup)


class TestPeriodPermissionGroup(TestCase):
    def test_grouptype_must_be_periodadmin(self):
        periodpermissiongroup = mommy.make(
            'devilry_account.PeriodPermissionGroup',
            permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        with self.assertRaisesMessage(ValidationError,
                                      'Only semesters can be added to semester administrator '
                                      'permission groups.'):
            periodpermissiongroup.clean()

    def test_only_single_editable_group_for_each_period_id_none(self):
        period1 = mommy.make('core.Period')
        period2 = mommy.make('core.Period')
        permissiongroup = mommy.make('devilry_account.PermissionGroup',
                                     grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN,
                                     is_custom_manageable=True)
        mommy.make('devilry_account.PeriodPermissionGroup',
                   permissiongroup=permissiongroup,
                   period=period1)
        with self.assertRaisesMessage(ValidationError, 'Only a single editable permission '
                                                       'group is allowed for a semester.'):
            mommy.prepare('devilry_account.PeriodPermissionGroup',
                          permissiongroup=permissiongroup,
                          period=period2).clean()

    def test_only_single_editable_group_for_each_period_id_not_none(self):
        period1 = mommy.make('core.Period')
        period2 = mommy.make('core.Period')
        permissiongroup = mommy.make('devilry_account.PermissionGroup',
                                     grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN,
                                     is_custom_manageable=True)
        mommy.make('devilry_account.PeriodPermissionGroup',
                   permissiongroup=permissiongroup,
                   period=period1)
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=period2)
        periodpermissiongroup.permissiongroup = permissiongroup
        with self.assertRaisesMessage(ValidationError, 'Only a single editable permission '
                                                       'group is allowed for a semester.'):
            periodpermissiongroup.clean()


class TestSubjectPermissionGroupQuerySet(TestCase):
    def test_user_is_departmentadmin_for_subject_false_not_in_any_subjectpermissiongroup(self):
        testsubject = mommy.make('core.Subject')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        self.assertFalse(SubjectPermissionGroup.objects.user_is_departmentadmin_for_subject(
            subject=testsubject, user=testuser))

    def test_user_is_departmentadmin_for_subject_true_for_departmentadmin(self):
        testsubject = mommy.make('core.Subject')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=mommy.make('devilry_account.SubjectPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN,
                                              subject=testsubject).permissiongroup)
        self.assertTrue(SubjectPermissionGroup.objects.user_is_departmentadmin_for_subject(
            subject=testsubject, user=testuser))

    def test_user_is_departmentadmin_for_subject_false_for_subjectadmin(self):
        testsubject = mommy.make('core.Subject')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=mommy.make('devilry_account.SubjectPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                              subject=testsubject).permissiongroup)
        self.assertFalse(SubjectPermissionGroup.objects.user_is_departmentadmin_for_subject(
            subject=testsubject, user=testuser))

    def test_user_is_subjectadmin_for_subject_false_not_in_any_subjectpermissiongroup(self):
        testsubject = mommy.make('core.Subject')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        self.assertFalse(SubjectPermissionGroup.objects.user_is_subjectadmin_for_subject(
            subject=testsubject, user=testuser))

    def test_user_is_subjectadmin_for_subject_false_for_departmentadmin(self):
        testsubject = mommy.make('core.Subject')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=mommy.make('devilry_account.SubjectPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN,
                                              subject=testsubject).permissiongroup)
        self.assertFalse(SubjectPermissionGroup.objects.user_is_subjectadmin_for_subject(
            subject=testsubject, user=testuser))

    def test_user_is_subjectadmin_for_subject_true_for_subjectadmin(self):
        testsubject = mommy.make('core.Subject')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=mommy.make('devilry_account.SubjectPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                              subject=testsubject).permissiongroup)
        self.assertTrue(SubjectPermissionGroup.objects.user_is_subjectadmin_for_subject(
            subject=testsubject, user=testuser))

    def test_get_devilryrole_for_user_on_subject_not_in_any_subjectpermissiongroup(self):
        testsubject = mommy.make('core.Subject')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        self.assertEqual(
            None,
            SubjectPermissionGroup.objects.get_devilryrole_for_user_on_subject(
                subject=testsubject, user=testuser))

    def test_get_devilryrole_for_user_on_subject_superuser(self):
        testsubject = mommy.make('core.Subject')
        testuser = mommy.make(settings.AUTH_USER_MODEL, is_superuser=True)
        self.assertEqual(
            'departmentadmin',
            SubjectPermissionGroup.objects.get_devilryrole_for_user_on_subject(
                subject=testsubject, user=testuser))

    def test_get_devilryrole_for_user_on_subject_departmentadmin(self):
        testsubject = mommy.make('core.Subject')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=mommy.make('devilry_account.SubjectPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN,
                                              subject=testsubject).permissiongroup)
        self.assertEqual(
            'departmentadmin',
            SubjectPermissionGroup.objects.get_devilryrole_for_user_on_subject(
                subject=testsubject, user=testuser))

    def test_get_devilryrole_for_user_on_subject_departmentadmin_even_if_also_subjectadmin(self):
        testsubject = mommy.make('core.Subject')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=mommy.make('devilry_account.SubjectPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                              subject=testsubject).permissiongroup)
        mommy.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=mommy.make('devilry_account.SubjectPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN,
                                              subject=testsubject).permissiongroup)
        self.assertEqual(
            'departmentadmin',
            SubjectPermissionGroup.objects.get_devilryrole_for_user_on_subject(
                subject=testsubject, user=testuser))

    def test_get_devilryrole_for_user_on_subject_subjectadmin(self):
        testsubject = mommy.make('core.Subject')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.PermissionGroupUser', user=testuser,
                   permissiongroup=mommy.make('devilry_account.SubjectPermissionGroup',
                                              permissiongroup__grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                              subject=testsubject).permissiongroup)
        self.assertEqual(
            'subjectadmin',
            SubjectPermissionGroup.objects.get_devilryrole_for_user_on_subject(
                subject=testsubject, user=testuser))

    def test_get_custom_managable_periodpermissiongroup_for_subject_only_custom_managable(self):
        testsubject = mommy.make('core.Subject')
        mommy.make('devilry_account.SubjectPermissionGroup',
                   permissiongroup__is_custom_manageable=False,
                   subject=testsubject)
        with self.assertRaises(SubjectPermissionGroup.DoesNotExist):
            SubjectPermissionGroup.objects.get_custom_managable_subjectpermissiongroup_for_subject(
                    subject=testsubject)

    def test_get_custom_managable_subjectpermissiongroup_for_subject_only_in_subject(self):
        testsubject = mommy.make('core.Subject')
        mommy.make('devilry_account.SubjectPermissionGroup',
                   permissiongroup__is_custom_manageable=True)
        with self.assertRaises(SubjectPermissionGroup.DoesNotExist):
            SubjectPermissionGroup.objects.get_custom_managable_subjectpermissiongroup_for_subject(
                    subject=testsubject)

    def test_get_custom_managable_subjectpermissiongroup_for_subject(self):
        testsubject = mommy.make('core.Subject')
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                           permissiongroup__is_custom_manageable=True,
                                           subject=testsubject)
        self.assertEqual(
            subjectpermissiongroup,
            SubjectPermissionGroup.objects.get_custom_managable_subjectpermissiongroup_for_subject(
                    subject=testsubject))

    def test_get_custom_managable_subjectpermissiongroup_for_subject_selectrelated_permissiongroup(self):
        testsubject = mommy.make('core.Subject')
        mommy.make('devilry_account.SubjectPermissionGroup',
                   permissiongroup__is_custom_manageable=True,
                   subject=testsubject)
        subjectpermissiongroup = SubjectPermissionGroup.objects.get_custom_managable_subjectpermissiongroup_for_subject(
            subject=testsubject)
        with self.assertNumQueries(0):
            str(subjectpermissiongroup.permissiongroup)


class TestSubjectPermissionGroup(TestCase):
    def test_grouptype_must_be_subjectadmin(self):
        subjectpermissiongroup = mommy.make(
            'devilry_account.SubjectPermissionGroup',
            permissiongroup__grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN)
        with self.assertRaisesMessage(ValidationError,
                                      'Courses can only be added to subject and '
                                      'department administrator permission groups.'):
            subjectpermissiongroup.clean()

    def test_only_single_editable_group_for_each_subject_id_none(self):
        subject1 = mommy.make('core.Subject')
        subject2 = mommy.make('core.Subject')
        permissiongroup = mommy.make('devilry_account.PermissionGroup',
                                     grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                     is_custom_manageable=True)
        mommy.make('devilry_account.SubjectPermissionGroup',
                   permissiongroup=permissiongroup,
                   subject=subject1)
        with self.assertRaisesMessage(ValidationError, 'Only a single editable permission '
                                                       'group is allowed for a course.'):
            mommy.prepare('devilry_account.SubjectPermissionGroup',
                          permissiongroup=permissiongroup,
                          subject=subject2).clean()

    def test_only_single_editable_group_for_each_subject_id_not_none(self):
        subject1 = mommy.make('core.Subject')
        subject2 = mommy.make('core.Subject')
        permissiongroup = mommy.make('devilry_account.PermissionGroup',
                                     grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                                     is_custom_manageable=True)
        mommy.make('devilry_account.SubjectPermissionGroup',
                   permissiongroup=permissiongroup,
                   subject=subject1)
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            subject=subject2)
        subjectpermissiongroup.permissiongroup = permissiongroup
        with self.assertRaisesMessage(ValidationError, 'Only a single editable permission '
                                                       'group is allowed for a course.'):
            subjectpermissiongroup.clean()
