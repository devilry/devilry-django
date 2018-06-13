from django import test
from django.conf import settings
from django.test import override_settings
from django.utils import timezone

from model_mommy import mommy

from devilry.devilry_merge_v3database.utils import user_merger
from django.contrib.auth import get_user_model
from devilry.devilry_account.models import UserEmail, UserName


class TestUserMerger(test.TestCase):
    from_db_alias = 'migrate_from'
    multi_db = True

    def test_sanity(self):
        mommy.make(settings.AUTH_USER_MODEL, shortname='defaultdbuser@example.com')
        mommy.prepare(settings.AUTH_USER_MODEL, shortname='migratedbuser@example.com').save(using=self.from_db_alias)

        # Test 'default' database
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(get_user_model().objects.get().shortname, 'defaultdbuser@example.com')

        # Test 'migrate_from' database
        self.assertEqual(get_user_model().objects.using(self.from_db_alias).count(), 1)
        self.assertEqual(get_user_model().objects.using(self.from_db_alias).get().shortname,
                         'migratedbuser@example.com')

    def test_check_migrated_user_fields(self):
        mommy.make(settings.AUTH_USER_MODEL, shortname='defaultdbuser@example.com')
        mommy.prepare(settings.AUTH_USER_MODEL, shortname='migratedbuser@example.com').save(using=self.from_db_alias)
        user_merger.UserMerger(from_db_alias=self.from_db_alias, transaction=True).run()

        merged_user = get_user_model().objects.get(shortname='migratedbuser@example.com')
        merged_from_user = get_user_model().objects.using(self.from_db_alias).get(shortname='migratedbuser@example.com')

        for field in merged_user._meta.fields:
            if field.name != 'id':
                self.assertEqual(getattr(merged_user, field.name), getattr(merged_from_user, field.name))

    def test_user_is_migrated(self):
        mommy.make(settings.AUTH_USER_MODEL, shortname='defaultdbuser@example.com')
        mommy.prepare(settings.AUTH_USER_MODEL, shortname='migratedbuser@example.com').save(using=self.from_db_alias)
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(get_user_model().objects.get().shortname, 'defaultdbuser@example.com')
        user_merger.UserMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(get_user_model().objects.count(), 2)
        self.assertTrue(get_user_model().objects.filter(shortname='migratedbuser@example.com').count(), 1)

    def test_multiple_users_are_migrated(self):
        mommy.make(settings.AUTH_USER_MODEL, shortname='defaultdbuser1@example.com')
        mommy.make(settings.AUTH_USER_MODEL, shortname='defaultdbuser2@example.com')
        mommy.prepare(settings.AUTH_USER_MODEL, shortname='migratedbuser1@example.com').save(using=self.from_db_alias)
        mommy.prepare(settings.AUTH_USER_MODEL, shortname='migratedbuser2@example.com').save(using=self.from_db_alias)
        mommy.prepare(settings.AUTH_USER_MODEL, shortname='migratedbuser3@example.com').save(using=self.from_db_alias)
        self.assertEqual(get_user_model().objects.count(), 2)
        self.assertEqual(get_user_model().objects.filter(shortname='defaultdbuser1@example.com').count(), 1)
        self.assertEqual(get_user_model().objects.filter(shortname='defaultdbuser2@example.com').count(), 1)

        user_merger.UserMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(get_user_model().objects.count(), 5)
        self.assertTrue(get_user_model().objects.filter(shortname='migratedbuser1@example.com').count(), 1)
        self.assertTrue(get_user_model().objects.filter(shortname='migratedbuser2@example.com').count(), 1)
        self.assertTrue(get_user_model().objects.filter(shortname='migratedbuser3@example.com').count(), 1)

    def test_check_migrated_users_fields(self):
        mommy.make(settings.AUTH_USER_MODEL, shortname='defaultdbuser1@example.com')
        mommy.make(settings.AUTH_USER_MODEL, shortname='defaultdbuser2@example.com')
        mommy.prepare(settings.AUTH_USER_MODEL, shortname='migratedbuser1@example.com').save(using=self.from_db_alias)
        mommy.prepare(settings.AUTH_USER_MODEL, shortname='migratedbuser2@example.com').save(using=self.from_db_alias)
        mommy.prepare(settings.AUTH_USER_MODEL, shortname='migratedbuser3@example.com').save(using=self.from_db_alias)
        user_merger.UserMerger(from_db_alias=self.from_db_alias, transaction=True).run()

        merged_users = get_user_model().objects.filter(shortname__startswith='migratedbuser')
        merged_from_users = get_user_model().objects.using(self.from_db_alias).all()
        self.assertEqual(merged_users.count(), 3)
        self.assertEqual(merged_from_users.count(), 3)

        for merged_user in merged_users:
            merged_from_user = merged_from_users.get(shortname=merged_user.shortname)
            for field in merged_user._meta.fields:
                if field.name != 'id':
                    self.assertEqual(getattr(merged_user, field.name), getattr(merged_from_user, field.name))

    def test_existing_user_not_migrated(self):
        mommy.make(settings.AUTH_USER_MODEL, shortname='user1@example.com')
        mommy.prepare(settings.AUTH_USER_MODEL, shortname='user1@example.com').save(using=self.from_db_alias)
        self.assertEqual(get_user_model().objects.count(), 1)
        user_merger.UserMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(get_user_model().objects.count(), 1)


class TestUserEmailMerger(test.TestCase):
    from_db_alias = 'migrate_from'
    multi_db = True

    def __mommy_make_migrate_user(self, **kwargs):
        mommy.prepare(settings.AUTH_USER_MODEL, **kwargs) \
            .save(using=self.from_db_alias)
        return get_user_model().objects.using(self.from_db_alias).filter(shortname=kwargs['shortname']).get()

    def __mommy_make_simulate_migrated_user(self, **kwargs):
        """
        Create a user in the `from_db_alias` database, and the same user in the default database to simulate that
        the user has been migrated.
        """
        migrate_user = self.__mommy_make_migrate_user(**kwargs)
        migrated_user = mommy.make(settings.AUTH_USER_MODEL, **kwargs)
        return migrated_user, migrate_user

    def test_sanity(self):
        default_user = mommy.make(settings.AUTH_USER_MODEL, shortname='user@example.com')
        migrate_from_user = self.__mommy_make_migrate_user(shortname='migrateuser@example.com')
        mommy.make('devilry_account.UserEmail', email='user@example.com', user=default_user)
        mommy.prepare('devilry_account.UserEmail', email='migrateuser@example.com', user=migrate_from_user)\
            .save(using=self.from_db_alias)

        # Test 'default' database
        self.assertEqual(UserEmail.objects.count(), 1)
        self.assertEqual(UserEmail.objects.get().email, 'user@example.com')

        # Test 'migrate_from' database
        self.assertEqual(UserEmail.objects.using(self.from_db_alias).count(), 1)
        self.assertEqual(UserEmail.objects.using(self.from_db_alias).get().email, 'migrateuser@example.com')

    def test_migrate_user_email_id_sanity(self):
        migrate_user = self.__mommy_make_migrate_user(id=230, shortname='migrateuser@example.com')
        migrated_user = mommy.make(settings.AUTH_USER_MODEL, shortname='migrateuser@example.com')
        mommy.prepare('devilry_account.UserEmail', email='migrateuser@example.com', user=migrate_user) \
            .save(using=self.from_db_alias)
        self.assertEqual(UserEmail.objects.count(), 0)
        self.assertEqual(UserEmail.objects.using(self.from_db_alias).get().user_id, 230)

        user_merger.UserEmailMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(UserEmail.objects.count(), 1)
        self.assertEqual(UserEmail.objects.using(self.from_db_alias).get().user_id, 230)
        self.assertEqual(UserEmail.objects.get().user_id, migrated_user.id)

    def test_migrate_user_email_fields(self):
        created_datetime = timezone.now() - timezone.timedelta(days=50)
        updated_datetime = timezone.now() - timezone.timedelta(days=25)
        migrate_user = self.__mommy_make_migrate_user(shortname='migrateuser@example.com')
        mommy.make(settings.AUTH_USER_MODEL, shortname='migrateuser@example.com')
        mommy.prepare('devilry_account.UserEmail',
                      is_primary=True,
                      use_for_notifications=False,
                      created_datetime=created_datetime,
                      last_updated_datetime=updated_datetime,
                      email='migrateuser@example.com',
                      user=migrate_user) \
            .save(using=self.from_db_alias)
        user_merger.UserEmailMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(UserEmail.objects.count(), 1)
        self.assertEqual(UserEmail.objects.get().created_datetime, created_datetime)
        self.assertEqual(UserEmail.objects.get().last_updated_datetime, updated_datetime)
        self.assertFalse(UserEmail.objects.get().use_for_notifications)
        self.assertTrue(UserEmail.objects.get().is_primary)

    def test_migrate_user_email(self):
        migrated_user, migrate_from_user = self.__mommy_make_simulate_migrated_user(
            shortname='migrateuser@example.com')
        mommy.prepare('devilry_account.UserEmail', email='migrateuser@example.com', user=migrate_from_user) \
            .save(using=self.from_db_alias)

        self.assertEqual(UserEmail.objects.count(), 0)
        user_merger.UserEmailMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(UserEmail.objects.count(), 1)
        user = get_user_model().objects.get(shortname='migrateuser@example.com')
        self.assertEqual(UserEmail.objects.get().user, user)

    def test_migrate_user_emails_for_different_users(self):
        migrated_user, migrate_user = self.__mommy_make_simulate_migrated_user(
            shortname='migrateuser1@example.com')
        mommy.prepare('devilry_account.UserEmail', email='migratemail1@example.com', user=migrate_user) \
            .save(using=self.from_db_alias)
        migrated_user, migrate_user = self.__mommy_make_simulate_migrated_user(
            shortname='migrateuser2@example.com')
        mommy.prepare('devilry_account.UserEmail', email='migratemail2@example.com', user=migrate_user) \
            .save(using=self.from_db_alias)
        migrated_user, migrate_user = self.__mommy_make_simulate_migrated_user(
            shortname='migrateuser3@example.com')
        mommy.prepare('devilry_account.UserEmail', email='migratemail3@example.com', user=migrate_user) \
            .save(using=self.from_db_alias)

        self.assertEqual(UserEmail.objects.count(), 0)
        user_merger.UserEmailMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(UserEmail.objects.count(), 3)
        self.assertEqual(
            UserEmail.objects.filter(
                user__shortname='migrateuser1@example.com', email='migratemail1@example.com').count(), 1)
        self.assertEqual(
            UserEmail.objects.filter(
                user__shortname='migrateuser2@example.com', email='migratemail2@example.com').count(), 1)
        self.assertEqual(
            UserEmail.objects.filter(
                user__shortname='migrateuser3@example.com', email='migratemail3@example.com').count(), 1)

    def test_migrate_user_emails_for_same_user(self):
        migrated_user, migrate_user = self.__mommy_make_simulate_migrated_user(
            shortname='migrateuser@example.com')
        mommy.prepare('devilry_account.UserEmail', email='migratemail1@example.com', user=migrate_user) \
            .save(using=self.from_db_alias)
        mommy.prepare('devilry_account.UserEmail', email='migratemail2@example.com', user=migrate_user) \
            .save(using=self.from_db_alias)
        mommy.prepare('devilry_account.UserEmail', email='migratemail3@example.com', user=migrate_user) \
            .save(using=self.from_db_alias)

        self.assertEqual(UserEmail.objects.count(), 0)
        user_merger.UserEmailMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(UserEmail.objects.count(), 3)
        for useremail in UserEmail.objects.all():
            self.assertEqual(useremail.user, migrated_user)

    def test_migrate_user_email_exists(self):
        user = mommy.make(settings.AUTH_USER_MODEL, shortname='user@example.com')
        mommy.make('devilry_account.UserEmail', email='user@example.com', user=user)
        migrate_user = self.__mommy_make_migrate_user(shortname='user@example.com')
        mommy.prepare('devilry_account.UserEmail', email='user@example.com', user=migrate_user) \
            .save(using=self.from_db_alias)

        self.assertEqual(UserEmail.objects.count(), 1)
        user_merger.UserEmailMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(UserEmail.objects.count(), 1)


@override_settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False)
class TestUserNameMerger(test.TestCase):
    from_db_alias = 'migrate_from'
    multi_db = True

    def __mommy_make_migrate_user(self, **kwargs):
        mommy.prepare(settings.AUTH_USER_MODEL, **kwargs) \
            .save(using=self.from_db_alias)
        return get_user_model().objects.using(self.from_db_alias).filter(shortname=kwargs['shortname']).get()

    def __mommy_make_simulate_migrated_user(self, **kwargs):
        """
        Create a user in the `from_db_alias` database, and the same user in the default database to simulate that
        the user has been migrated.
        """
        migrate_user = self.__mommy_make_migrate_user(**kwargs)
        migrated_user = mommy.make(settings.AUTH_USER_MODEL, **kwargs)
        return migrated_user, migrate_user

    def test_sanity(self):
        default_user = mommy.make(settings.AUTH_USER_MODEL, shortname='user@example.com')
        migrate_from_user = self.__mommy_make_migrate_user(shortname='migrateuser@example.com')
        mommy.make('devilry_account.UserName', username='user', user=default_user)
        mommy.prepare('devilry_account.UserName', username='migrateuser', user=migrate_from_user)\
            .save(using=self.from_db_alias)

        # Test 'default' database
        self.assertEqual(UserName.objects.count(), 1)
        self.assertEqual(UserName.objects.get().username, 'user')

        # Test 'migrate_from' database
        self.assertEqual(UserName.objects.using(self.from_db_alias).count(), 1)
        self.assertEqual(UserName.objects.using(self.from_db_alias).get().username, 'migrateuser')

    def test_migrate_username_id_sanity(self):
        migrate_user = self.__mommy_make_migrate_user(id=230, shortname='migrateuser@example.com')
        migrated_user = mommy.make(settings.AUTH_USER_MODEL, shortname='migrateuser@example.com')
        mommy.prepare('devilry_account.UserName', username='migrateuser', user=migrate_user) \
            .save(using=self.from_db_alias)
        self.assertEqual(UserName.objects.count(), 0)
        self.assertEqual(UserName.objects.using(self.from_db_alias).get().user_id, 230)

        user_merger.UserNameMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(UserName.objects.count(), 1)
        self.assertEqual(UserName.objects.using(self.from_db_alias).get().user_id, 230)
        self.assertEqual(UserName.objects.get().user_id, migrated_user.id)

    def test_migrate_username_fields(self):
        created_datetime = timezone.now() - timezone.timedelta(days=50)
        updated_datetime = timezone.now() - timezone.timedelta(days=25)
        migrate_user = self.__mommy_make_migrate_user(shortname='migrateuser@example.com')
        mommy.make(settings.AUTH_USER_MODEL, shortname='migrateuser@example.com')
        mommy.prepare('devilry_account.UserName',
                      is_primary=True,
                      created_datetime=created_datetime,
                      last_updated_datetime=updated_datetime,
                      username='migrateuser',
                      user=migrate_user) \
            .save(using=self.from_db_alias)
        user_merger.UserNameMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(UserName.objects.count(), 1)
        self.assertEqual(UserName.objects.get().created_datetime, created_datetime)
        self.assertEqual(UserName.objects.get().last_updated_datetime, updated_datetime)
        self.assertTrue(UserName.objects.get().is_primary)

    def test_migrate_useremail(self):
        migrated_user, migrate_from_user = self.__mommy_make_simulate_migrated_user(
            shortname='migrateuser@example.com')
        mommy.prepare('devilry_account.UserName', username='migrateuser', user=migrate_from_user) \
            .save(using=self.from_db_alias)

        self.assertEqual(UserName.objects.count(), 0)
        user_merger.UserNameMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(UserName.objects.count(), 1)
        user = get_user_model().objects.get(shortname='migrateuser@example.com')
        self.assertEqual(UserName.objects.get().user, user)

    def test_migrate_usernames_for_different_users(self):
        migrated_user, migrate_user = self.__mommy_make_simulate_migrated_user(
            shortname='migrateuser1@example.com')
        mommy.prepare('devilry_account.UserName', username='migrateuser1', user=migrate_user) \
            .save(using=self.from_db_alias)
        migrated_user, migrate_user = self.__mommy_make_simulate_migrated_user(
            shortname='migrateuser2@example.com')
        mommy.prepare('devilry_account.UserName', username='migrateuser2', user=migrate_user) \
            .save(using=self.from_db_alias)
        migrated_user, migrate_user = self.__mommy_make_simulate_migrated_user(
            shortname='migrateuser3@example.com')
        mommy.prepare('devilry_account.UserName', username='migrateuser3', user=migrate_user) \
            .save(using=self.from_db_alias)

        self.assertEqual(UserName.objects.count(), 0)
        user_merger.UserNameMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(UserName.objects.count(), 3)
        self.assertEqual(
            UserName.objects.filter(user__shortname='migrateuser1@example.com', username='migrateuser1').count(), 1)
        self.assertEqual(
            UserName.objects.filter(user__shortname='migrateuser2@example.com', username='migrateuser2').count(), 1)
        self.assertEqual(
            UserName.objects.filter(user__shortname='migrateuser3@example.com', username='migrateuser3').count(), 1)

    def test_migrate_usernames_for_same_user(self):
        migrated_user, migrate_user = self.__mommy_make_simulate_migrated_user(
            shortname='migrateuser@example.com')
        mommy.prepare('devilry_account.UserName', username='migrateuser1', user=migrate_user) \
            .save(using=self.from_db_alias)
        mommy.prepare('devilry_account.UserName', username='migrateuser2', user=migrate_user) \
            .save(using=self.from_db_alias)
        mommy.prepare('devilry_account.UserName', username='migrateuser3', user=migrate_user) \
            .save(using=self.from_db_alias)

        self.assertEqual(UserName.objects.count(), 0)
        user_merger.UserNameMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(UserName.objects.count(), 3)
        for username in UserName.objects.all():
            self.assertEqual(username.user, migrated_user)

    def test_migrate_user_email_exists(self):
        user = mommy.make(settings.AUTH_USER_MODEL, shortname='user@example.com')
        mommy.make('devilry_account.UserName', username='user', user=user, is_primary=True)
        migrate_user = self.__mommy_make_migrate_user(shortname='user@example.com')
        mommy.prepare('devilry_account.UserName', username='user', user=migrate_user, is_primary=None) \
            .save(using=self.from_db_alias)

        self.assertEqual(UserName.objects.count(), 1)
        user_merger.UserNameMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(UserName.objects.count(), 1)
        self.assertTrue(UserName.objects.get().is_primary)
        self.assertIsNone(UserName.objects.using(self.from_db_alias).get().is_primary)
