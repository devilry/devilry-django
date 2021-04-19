

from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import management
from django.utils import timezone
from model_bakery import baker

from devilry.devilry_account.models import PermissionGroup
from devilry.utils import datetimeutils
from devilry.devilry_superadmin.management.commands.devilry_delete_inactive_users import InactiveUserDeleter


class TestDeleteInactiveUsersCommand(test.TestCase):
    def __run_management_command(self, iso_datetime_string):
        management.call_command(
            'devilry_delete_inactive_users',
            '--inactive-since-datetime={}'.format(iso_datetime_string))

    def test_aborted_no_users(self):
        iso_datetime_string = '2018-01-01 20:00:00'
        with self.assertRaises(SystemExit):
            self.__run_management_command(iso_datetime_string=iso_datetime_string)

    def test_aborted_no_inactive_users(self):
        iso_datetime_string = '2019-01-01 10:00:00'
        baker.make(settings.AUTH_USER_MODEL, last_login=datetimeutils.from_isoformat(iso_datetime_string))
        with self.assertRaises(SystemExit):
            self.__run_management_command(iso_datetime_string='2018-01-01 10:00:00')

    def test_aborted_last_login_same_as_datetime_iso_argument(self):
        iso_datetime_string = '2019-01-01 10:00:00'
        baker.make(settings.AUTH_USER_MODEL, last_login=datetimeutils.from_isoformat(iso_datetime_string))
        with self.assertRaises(SystemExit):
            self.__run_management_command(iso_datetime_string='2019-01-01 10:00:00')


class TestInactiveUserDeleter(test.TestCase):
    def __create_timestamp(self, year=2019, month=1, day=1, hour=0, minute=0, second=0, microsecond=0):
        return timezone.now().replace(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            microsecond=microsecond
        )

    def test_no_users(self):
        inactive_since = self.__create_timestamp(year=2018, hour=10)
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 0)

    def test_no_inactive_users(self):
        inactive_since = self.__create_timestamp(year=2018, hour=10)
        baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2019, hour=10))
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 0)

    def test_last_login_same_as_datetime_iso_argument(self):
        inactive_since = self.__create_timestamp(year=2018, hour=10)
        baker.make(settings.AUTH_USER_MODEL, last_login=inactive_since)
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 0)

    def test_last_login_null_not_to_be_deleted(self):
        inactive_since = self.__create_timestamp(year=2019, hour=10)
        baker.make(settings.AUTH_USER_MODEL)
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 0)

    def test_last_login_one_second_before(self):
        inactive_since = self.__create_timestamp(year=2019, hour=10, minute=0, second=1)
        baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2019, hour=10, minute=0, second=0))
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 1)

    def test_last_login_one_second_before_multiple_users(self):
        inactive_since = self.__create_timestamp(year=2019, hour=10, minute=0, second=1)
        baker.make(settings.AUTH_USER_MODEL,
                   last_login=self.__create_timestamp(year=2019, hour=10, minute=0, second=0), _quantity=10)
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 10)

    def test_last_login_one_second_after(self):
        inactive_since = self.__create_timestamp(year=2019, hour=10, minute=0, second=1)
        baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2019, hour=10, minute=0, second=2))
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 0)

    def test_last_login_one_microsecond_after(self):
        inactive_since = self.__create_timestamp(year=2019, hour=10, minute=0, second=0)
        baker.make(settings.AUTH_USER_MODEL,
                   last_login=self.__create_timestamp(year=2019, hour=10, minute=0, second=0, microsecond=1))
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 0)

    def test_last_login_one_microsecond_before(self):
        inactive_since = self.__create_timestamp(year=2019, hour=10, minute=0, second=0, microsecond=2)
        baker.make(settings.AUTH_USER_MODEL,
                   last_login=self.__create_timestamp(year=2019, hour=10, minute=0, second=0, microsecond=1))
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 1)

    def test_user_is_superuser(self):
        inactive_since = self.__create_timestamp(year=2018, hour=10)
        baker.make(settings.AUTH_USER_MODEL, is_superuser=True, last_login=self.__create_timestamp(year=2017, hour=10))
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 0)

    def test_user_registered_as_student_on_active_semester(self):
        inactive_since = self.__create_timestamp(year=2018, hour=10)
        user = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        period = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.RelatedStudent', period=period, user=user)
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 0)

    def test_user_registered_as_examiner_on_active_semester(self):
        inactive_since = self.__create_timestamp(year=2018, hour=10)
        user = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        period = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.RelatedExaminer', period=period, user=user)
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 0)

    def __make_period_admin(self, period, user):
        permission_group = baker.make('devilry_account.PermissionGroup',
                                      grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN)
        baker.make('devilry_account.PermissionGroupUser', user=user, permissiongroup=permission_group)
        baker.make('devilry_account.PeriodPermissionGroup', period=period, permissiongroup=permission_group)

    def test_user_registered_as_period_admin_on_active_semester(self):
        inactive_since = self.__create_timestamp(year=2018, hour=10)
        user = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        period = baker.make_recipe('devilry.apps.core.period_active')
        self.__make_period_admin(period=period, user=user)
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 0)

    def test_with_students_examiners_admins_on_active_period(self):
        inactive_since = self.__create_timestamp(year=2018, hour=10)
        student_user = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        examiner_user = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        admin_user = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        period = baker.make_recipe('devilry.apps.core.period_active')
        self.__make_period_admin(period=period, user=admin_user)
        baker.make('core.RelatedStudent', period=period, user=student_user)
        baker.make('core.RelatedExaminer', period=period, user=examiner_user)
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 0)

    def test_with_students_examiners_admins_on_inactive_period(self):
        inactive_since = self.__create_timestamp(year=2018, hour=10)
        admin_user = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        student_user = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        examiner_user = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        period = baker.make_recipe('devilry.apps.core.period_old')
        self.__make_period_admin(period=period, user=admin_user)
        baker.make('core.RelatedStudent', period=period, user=student_user)
        baker.make('core.RelatedExaminer', period=period, user=examiner_user)
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 3)

    def test_delete_student(self):
        inactive_since = self.__create_timestamp(year=2018, hour=10)
        student_user = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        period = baker.make_recipe('devilry.apps.core.period_old')
        baker.make('core.RelatedStudent', period=period, user=student_user)
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 1)
        user_deleter.delete()
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_delete_multiple_students(self):
        inactive_since = self.__create_timestamp(year=2018, hour=10)
        student_user1 = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        student_user2 = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        period = baker.make_recipe('devilry.apps.core.period_old')
        baker.make('core.RelatedStudent', period=period, user=student_user1)
        baker.make('core.RelatedStudent', period=period, user=student_user2)
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 2)
        user_deleter.delete()
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_delete_examiner(self):
        inactive_since = self.__create_timestamp(year=2018, hour=10)
        examiner_user = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        period = baker.make_recipe('devilry.apps.core.period_old')
        baker.make('core.RelatedExaminer', period=period, user=examiner_user)
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 1)
        user_deleter.delete()
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_delete_multiple_examiners(self):
        inactive_since = self.__create_timestamp(year=2018, hour=10)
        examiner_user1 = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        examiner_user2 = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        period = baker.make_recipe('devilry.apps.core.period_old')
        baker.make('core.RelatedExaminer', period=period, user=examiner_user1)
        baker.make('core.RelatedExaminer', period=period, user=examiner_user2)
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 2)
        user_deleter.delete()
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_delete_period_admin(self):
        inactive_since = self.__create_timestamp(year=2018, hour=10)
        admin_user = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        period = baker.make_recipe('devilry.apps.core.period_old')
        self.__make_period_admin(period=period, user=admin_user)
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 1)
        user_deleter.delete()
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_delete_multiple_period_admins(self):
        inactive_since = self.__create_timestamp(year=2018, hour=10)
        admin_user1 = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        admin_user2 = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        period = baker.make_recipe('devilry.apps.core.period_old')
        self.__make_period_admin(period=period, user=admin_user1)
        self.__make_period_admin(period=period, user=admin_user2)
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 2)
        user_deleter.delete()
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_only_users_last_login_before_timestamp_deleted_sanity(self):
        inactive_since = self.__create_timestamp(year=2018, hour=10)
        user1 = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2018, hour=10))
        user2 = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2017, hour=10))
        user3 = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2018, hour=11))
        user4 = baker.make(settings.AUTH_USER_MODEL, last_login=self.__create_timestamp(year=2016, hour=10))
        user_deleter = InactiveUserDeleter(inactive_since)
        self.assertEqual(user_deleter.get_users_to_delete_queryset().count(), 2)
        user_deleter.delete()
        user_queryset = get_user_model().objects.all()
        self.assertEqual(user_queryset.count(), 2)
        self.assertNotIn(user2, user_queryset)
        self.assertNotIn(user4, user_queryset)
        self.assertIn(user1, user_queryset)
        self.assertIn(user3, user_queryset)

