from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import override_settings
from django.utils import timezone

from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_account import models as account_models
from devilry.devilry_merge_v3database.utils import period_merger


class TestPeriodMerger(test.TestCase):
    from_db_alias = 'migrate_from'
    multi_db = True

    def __create_period_with_subject_in_default_database(self, period_short_name, subject_short_name,
                                                         extra_period_kwargs=None):
        """
        Create period with subject in default database
        """
        subject = mommy.make('core.Subject', short_name=subject_short_name)
        if extra_period_kwargs:
            mommy.make('core.Period', short_name=period_short_name, parentnode=subject, **extra_period_kwargs)
        else:
            mommy.make('core.Period', short_name=period_short_name, parentnode=subject)

    def __create_period_with_subject_in_migrate_database(self, period_short_name, subject_short_name,
                                                         extra_period_kwargs=None):
        """
        Create period with subject in migrate database
        """
        subject = mommy.prepare('core.Subject', short_name=subject_short_name)
        subject.save(using=self.from_db_alias)
        if extra_period_kwargs:
            mommy.prepare('core.Period', short_name=period_short_name, parentnode=subject, **extra_period_kwargs)\
                .save(using=self.from_db_alias)
        else:
            mommy.prepare('core.Period', short_name=period_short_name, parentnode=subject)\
                .save(using=self.from_db_alias)

    def test_database_sanity(self):
        # Default database data
        self.__create_period_with_subject_in_default_database(
            period_short_name='default_period', subject_short_name='default_subject')

        # Migrate database data
        self.__create_period_with_subject_in_migrate_database(
            period_short_name='migrate_period', subject_short_name='migrate_subject')

        # Test default database
        self.assertEqual(core_models.Period.objects.count(), 1)
        self.assertEqual(core_models.Subject.objects.count(), 1)
        self.assertEqual(core_models.Subject.objects.get().short_name, 'default_subject')
        self.assertEqual(core_models.Period.objects.get().short_name, 'default_period')

        # Test migrate database
        self.assertEqual(core_models.Period.objects.using(self.from_db_alias).count(), 1)
        self.assertEqual(core_models.Subject.objects.using(self.from_db_alias).count(), 1)
        self.assertEqual(core_models.Subject.objects.using(self.from_db_alias).get().short_name, 'migrate_subject')
        self.assertEqual(core_models.Period.objects.using(self.from_db_alias).get().short_name, 'migrate_period')

    def test_check_existing_periods_not_affected(self):
        # Default database data
        default_start_time = timezone.now() - timezone.timedelta(days=50)
        default_end_time = timezone.now() + timezone.timedelta(days=50)
        default_etag = timezone.now() - timezone.timedelta(days=20)
        default_period_kwargs = {
            'long_name': 'Default Period',
            'start_time': default_start_time,
            'end_time': default_end_time,
        }
        self.__create_period_with_subject_in_default_database(
            period_short_name='default_period', subject_short_name='default_subject',
            extra_period_kwargs=default_period_kwargs)
        core_models.Period.objects.filter(short_name='default_period')\
            .update(etag=default_etag)
        mommy.make('core.Subject', short_name='migrate_subject')

        # Migrate database data
        migrate_start_time = timezone.now() - timezone.timedelta(days=200)
        migrate_end_time = timezone.now() - timezone.timedelta(days=100)
        migrate_etag = timezone.now() - timezone.timedelta(days=120)
        migrate_period_kwargs = {
            'long_name': 'Migrate Period',
            'start_time': migrate_start_time,
            'end_time': migrate_end_time,
        }
        self.__create_period_with_subject_in_migrate_database(
            period_short_name='migrate_period', subject_short_name='migrate_subject',
            extra_period_kwargs=migrate_period_kwargs)
        core_models.Period.objects.using(self.from_db_alias).filter(short_name='migrate_period')\
            .update(etag=migrate_etag)

        period_merger.PeriodMerger(from_db_alias=self.from_db_alias, transaction=True).run()

        # Test default data
        default_period = core_models.Period.objects.get(short_name='default_period')
        self.assertEqual(default_period.long_name, 'Default Period')
        self.assertEqual(default_period.subject.short_name, 'default_subject')
        self.assertEqual(default_period.start_time, default_start_time)
        self.assertEqual(default_period.end_time, default_end_time)
        self.assertEqual(default_period.etag, default_etag)

        # Test default data
        migrate_period = core_models.Period.objects.get(short_name='migrate_period')
        self.assertEqual(migrate_period.long_name, 'Migrate Period')
        self.assertEqual(migrate_period.subject.short_name, 'migrate_subject')
        self.assertEqual(migrate_period.start_time, migrate_start_time)
        self.assertEqual(migrate_period.end_time, migrate_end_time)
        self.assertEqual(migrate_period.etag, migrate_etag)

    def test_subject_not_imported(self):
        # Default database data
        self.__create_period_with_subject_in_default_database(
            period_short_name='default_period', subject_short_name='default_subject')

        # Migrate database data
        self.__create_period_with_subject_in_migrate_database(
            period_short_name='migrate_period', subject_short_name='migrate_subject')

        with self.assertRaisesMessage(ValueError, 'Subjects must be imported before Periods.'):
            period_merger.PeriodMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_period_imported(self):
        # Default database data
        mommy.make('core.Subject', short_name='migrate_subject')

        # Migrate database data
        self.__create_period_with_subject_in_migrate_database(
            period_short_name='migrate_period', subject_short_name='migrate_subject')

        self.assertEqual(core_models.Period.objects.count(), 0)
        period_merger.PeriodMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.Period.objects.count(), 1)

    def test_multiple_periods_imported_with_one_subject_each(self):
        # Default database data
        mommy.make('core.Subject', short_name='migrate_subject1')
        mommy.make('core.Subject', short_name='migrate_subject2')
        mommy.make('core.Subject', short_name='migrate_subject3')

        # Migrate database data
        self.__create_period_with_subject_in_migrate_database(
            period_short_name='migrate_period1', subject_short_name='migrate_subject1')
        self.__create_period_with_subject_in_migrate_database(
            period_short_name='migrate_period2', subject_short_name='migrate_subject2')
        self.__create_period_with_subject_in_migrate_database(
            period_short_name='migrate_period3', subject_short_name='migrate_subject3')

        self.assertEqual(core_models.Subject.objects.count(), 3)
        self.assertEqual(core_models.Period.objects.count(), 0)
        period_merger.PeriodMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.Period.objects.count(), 3)
        self.assertEqual(core_models.Period.objects.filter(parentnode__short_name='migrate_subject1').count(), 1)
        self.assertEqual(core_models.Period.objects.filter(parentnode__short_name='migrate_subject2').count(), 1)
        self.assertEqual(core_models.Period.objects.filter(parentnode__short_name='migrate_subject3').count(), 1)

    def test_multiple_periods_imported_on_multiple_subjects(self):
        # Default database data
        mommy.make('core.Subject', short_name='migrate_subject1')
        mommy.make('core.Subject', short_name='migrate_subject2')
        mommy.make('core.Subject', short_name='migrate_subject3')

        # Migrate database data
        subject1 = mommy.prepare('core.Subject', short_name='migrate_subject1')
        subject1.save(using=self.from_db_alias)
        mommy.prepare('core.Period', short_name='migrate_period1', parentnode=subject1).save(using=self.from_db_alias)
        mommy.prepare('core.Period', short_name='migrate_period2', parentnode=subject1).save(using=self.from_db_alias)

        subject2 = mommy.prepare('core.Subject', short_name='migrate_subject2')
        subject2.save(using=self.from_db_alias)
        mommy.prepare('core.Period', short_name='migrate_period3', parentnode=subject2).save(using=self.from_db_alias)
        mommy.prepare('core.Period', short_name='migrate_period4', parentnode=subject2).save(using=self.from_db_alias)

        subject3 = mommy.prepare('core.Subject', short_name='migrate_subject3')
        subject3.save(using=self.from_db_alias)
        mommy.prepare('core.Period', short_name='migrate_period5', parentnode=subject3).save(using=self.from_db_alias)
        mommy.prepare('core.Period', short_name='migrate_period6', parentnode=subject3).save(using=self.from_db_alias)

        self.assertEqual(core_models.Subject.objects.count(), 3)
        self.assertEqual(core_models.Period.objects.count(), 0)
        period_merger.PeriodMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.Period.objects.count(), 6)
        self.assertEqual(core_models.Period.objects.filter(parentnode__short_name='migrate_subject1').count(), 2)
        self.assertEqual(core_models.Period.objects.filter(parentnode__short_name='migrate_subject2').count(), 2)
        self.assertEqual(core_models.Period.objects.filter(parentnode__short_name='migrate_subject3').count(), 2)
        self.assertEqual(core_models.Period.objects.filter(short_name='migrate_period1').get().parentnode.short_name,
                         'migrate_subject1')
        self.assertEqual(core_models.Period.objects.filter(short_name='migrate_period2').get().parentnode.short_name,
                         'migrate_subject1')
        self.assertEqual(core_models.Period.objects.filter(short_name='migrate_period3').get().parentnode.short_name,
                         'migrate_subject2')
        self.assertEqual(core_models.Period.objects.filter(short_name='migrate_period4').get().parentnode.short_name,
                         'migrate_subject2')
        self.assertEqual(core_models.Period.objects.filter(short_name='migrate_period5').get().parentnode.short_name,
                         'migrate_subject3')
        self.assertEqual(core_models.Period.objects.filter(short_name='migrate_period6').get().parentnode.short_name,
                         'migrate_subject3')

    def test_periods_on_subject_can_not_have_same_short_name_validation_error_raised(self):
        # Default database data
        subject = mommy.make('core.Subject', short_name='migrate_subject')
        mommy.make('core.Period', short_name='period', parentnode=subject)

        # Migrate database data
        self.__create_period_with_subject_in_migrate_database(
            period_short_name='period', subject_short_name='migrate_subject')

        with self.assertRaises(ValidationError):
            period_merger.PeriodMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_periods_can_have_same_short_name_across_subjects_no_validation_error_raised(self):
        # Default database data
        subject = mommy.make('core.Subject', short_name='migrate_subject')
        mommy.make('core.Period', short_name='period')

        # Migrate database data
        self.__create_period_with_subject_in_migrate_database(
            period_short_name='period', subject_short_name='migrate_subject')
        period_merger.PeriodMerger(from_db_alias=self.from_db_alias, transaction=True).run()


class TestPeriodPermissionGroupMerger(test.TestCase):
    from_db_alias = 'migrate_from'
    multi_db = True

    def __create_period_permission_groups_in_default_database(self, subject_short_name, period_short_name,
                                                              permissiongroup_name, with_period_permission_group=False):
        """
        Create Subject, Period, PermissionGroup and PeriodPermissionGroup in database to migrate from.
        """
        pmgroup = mommy.make('devilry_account.PermissionGroup', name=permissiongroup_name,
                             grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN)
        subject = mommy.make('core.Subject', short_name=subject_short_name)
        period = mommy.make('core.Period', parentnode=subject, short_name=period_short_name)
        if with_period_permission_group:
            mommy.make('devilry_account.PeriodPermissionGroup', period=period,
                       permissiongroup=pmgroup)

    def __create_period_permission_groups_in_migrate_database(self, subject_short_name, period_short_name,
                                                              permissiongroup_name):
        """
        Create Subject, Period, PermissionGroup and PeriodPermissionGroup in database to migrate from.
        """
        pmgroup = mommy.prepare('devilry_account.PermissionGroup', name=permissiongroup_name,
                                        grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN)
        pmgroup.save(using=self.from_db_alias)
        subject = mommy.prepare('core.Subject', short_name=subject_short_name)
        subject.save(using=self.from_db_alias)
        period = mommy.prepare('core.Period', short_name=period_short_name, parentnode=subject)
        period.save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PeriodPermissionGroup', period=period,
                      permissiongroup=pmgroup).save(using=self.from_db_alias)

    def test_database_sanity(self):
        # Default database data
        self.__create_period_permission_groups_in_default_database(
            subject_short_name='default_subject', period_short_name='default_period',
            permissiongroup_name='default_pmgroup', with_period_permission_group=True)

        # Migrate database data
        self.__create_period_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject', period_short_name='migrate_period',
            permissiongroup_name='migrate_pmgroup')

        # Test default database
        self.assertEqual(account_models.PermissionGroup.objects.count(), 1)
        self.assertEqual(account_models.PeriodPermissionGroup.objects.count(), 1)
        self.assertEqual(core_models.Subject.objects.count(), 1)
        self.assertEqual(core_models.Period.objects.count(), 1)
        self.assertEqual(account_models.PeriodPermissionGroup.objects.get().permissiongroup.name, 'default_pmgroup')
        self.assertEqual(account_models.PeriodPermissionGroup.objects.get().period.short_name, 'default_period')

        # Test default database
        self.assertEqual(account_models.PermissionGroup.objects.using(self.from_db_alias).count(), 1)
        self.assertEqual(account_models.PeriodPermissionGroup.objects.using(self.from_db_alias).count(), 1)
        self.assertEqual(core_models.Subject.objects.using(self.from_db_alias).count(), 1)
        self.assertEqual(core_models.Period.objects.using(self.from_db_alias).count(), 1)
        periodperimissiongroup_queryset = account_models.PeriodPermissionGroup.objects.using(self.from_db_alias)
        self.assertEqual(periodperimissiongroup_queryset.get().permissiongroup.name, 'migrate_pmgroup')
        self.assertEqual(periodperimissiongroup_queryset.get().period.short_name, 'migrate_period')

    def test_check_existing_period_permission_group_not_affected(self):
        # Default database data
        self.__create_period_permission_groups_in_default_database(
            subject_short_name='default_subject', period_short_name='default_period',
            permissiongroup_name='default_pmgroup', with_period_permission_group=True)
        self.__create_period_permission_groups_in_default_database(
            subject_short_name='migrate_subject', period_short_name='migrate_period',
            permissiongroup_name='migrate_pmgroup')

        # Migrate database data
        self.__create_period_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject', period_short_name='migrate_period',
            permissiongroup_name='migrate_pmgroup')

        self.assertEqual(account_models.PeriodPermissionGroup.objects.count(), 1)
        period_merger.PeriodPermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(account_models.PeriodPermissionGroup.objects.count(), 2)
        default_period_pmgroup = account_models.PeriodPermissionGroup.objects\
            .get(permissiongroup__name='default_pmgroup')
        self.assertEqual(default_period_pmgroup.period.short_name, 'default_period')
        self.assertEqual(default_period_pmgroup.period.parentnode.short_name, 'default_subject')
        migrated_period_pmgroup = account_models.PeriodPermissionGroup.objects\
            .get(permissiongroup__name='migrate_pmgroup')
        self.assertEqual(migrated_period_pmgroup.period.short_name, 'migrate_period')
        self.assertEqual(migrated_period_pmgroup.period.parentnode.short_name, 'migrate_subject')

    def test_period_not_imported(self):
        # Default database data
        mommy.make('core.Subject', short_name='migrate_subject')
        mommy.make('devilry_account.PermissionGroup', name='migrate_pmgroup')

        # Migrate database data
        self.__create_period_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject',
            period_short_name='migrate_period', permissiongroup_name='migrate_pmgroup'
        )

        with self.assertRaisesMessage(ValueError,
                                      'Periods and PermissionGroups must be imported before PeriodPermissionGroups'):
            period_merger.PeriodPermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_permissiongroup_not_imported(self):
        # Default database data
        subject = mommy.make('core.Subject', short_name='migrate_subject')
        mommy.make('core.Period', parentnode=subject, short_name='migrate_period')

        # Migrate database data
        self.__create_period_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject',
            period_short_name='migrate_period', permissiongroup_name='migrate_pmgroup'
        )

        with self.assertRaisesMessage(ValueError,
                                      'Periods and PermissionGroups must be imported before PeriodPermissionGroups'):
            period_merger.PeriodPermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_period_permission_group_imported(self):
        # Default database data
        self.__create_period_permission_groups_in_default_database(
            subject_short_name='migrate_subject', period_short_name='migrate_period',
            permissiongroup_name='migrate_pmgroup')

        # Migrate database data
        self.__create_period_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject', period_short_name='migrate_period',
            permissiongroup_name='migrate_pmgroup')

        self.assertEqual(account_models.PeriodPermissionGroup.objects.count(), 0)
        period_merger.PeriodPermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(account_models.PeriodPermissionGroup.objects.count(), 1)
        period_permission_group = account_models.PeriodPermissionGroup.objects.get()
        self.assertEqual(period_permission_group.period.parentnode.short_name, 'migrate_subject')
        self.assertEqual(period_permission_group.period.short_name, 'migrate_period')
        self.assertEqual(period_permission_group.permissiongroup.name, 'migrate_pmgroup')

    def test_multiple_period_permission_groups_imported(self):
        # Default database data
        self.__create_period_permission_groups_in_default_database(
            subject_short_name='migrate_subject1', period_short_name='migrate_period1',
            permissiongroup_name='migrate_pmgroup1')
        self.__create_period_permission_groups_in_default_database(
            subject_short_name='migrate_subject2', period_short_name='migrate_period2',
            permissiongroup_name='migrate_pmgroup2')
        self.__create_period_permission_groups_in_default_database(
            subject_short_name='migrate_subject3', period_short_name='migrate_period3',
            permissiongroup_name='migrate_pmgroup3')

        # Migrate database data
        self.__create_period_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject1', period_short_name='migrate_period1',
            permissiongroup_name='migrate_pmgroup1')
        self.__create_period_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject2', period_short_name='migrate_period2',
            permissiongroup_name='migrate_pmgroup2')
        self.__create_period_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject3', period_short_name='migrate_period3',
            permissiongroup_name='migrate_pmgroup3')

        self.assertEqual(account_models.PeriodPermissionGroup.objects.count(), 0)
        period_merger.PeriodPermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(account_models.PeriodPermissionGroup.objects.count(), 3)
        period_pmgroup1 = account_models.PeriodPermissionGroup.objects.get(permissiongroup__name='migrate_pmgroup1')
        self.assertEqual(period_pmgroup1.period.parentnode.short_name, 'migrate_subject1')
        self.assertEqual(period_pmgroup1.period.short_name, 'migrate_period1')
        period_pmgroup2 = account_models.PeriodPermissionGroup.objects.get(permissiongroup__name='migrate_pmgroup2')
        self.assertEqual(period_pmgroup2.period.parentnode.short_name, 'migrate_subject2')
        self.assertEqual(period_pmgroup2.period.short_name, 'migrate_period2')
        period_pmgroup3 = account_models.PeriodPermissionGroup.objects.get(permissiongroup__name='migrate_pmgroup3')
        self.assertEqual(period_pmgroup3.period.parentnode.short_name, 'migrate_subject3')
        self.assertEqual(period_pmgroup3.period.short_name, 'migrate_period3')

    def test_period_permission_groups_on_same_period_raises_validation_error(self):
        # Default database data
        self.__create_period_permission_groups_in_default_database(
            subject_short_name='subject', period_short_name='period', permissiongroup_name='pmgroup',
            with_period_permission_group=True)

        # Migrate database data
        self.__create_period_permission_groups_in_migrate_database(
            subject_short_name='subject', period_short_name='period', permissiongroup_name='pmgroup')
        with self.assertRaises(ValidationError):
            period_merger.PeriodPermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_migrated_user_is_admin_on_period_after_import(self):
        # Default database data
        self.__create_period_permission_groups_in_default_database(
            subject_short_name='default_subject', period_short_name='default_period',
            permissiongroup_name='default_pmgroup', with_period_permission_group=True)
        default_user = mommy.make(settings.AUTH_USER_MODEL, shortname='default_user')
        mommy.make('devilry_account.PermissionGroupUser', user=default_user,
                   permissiongroup=account_models.PermissionGroup.objects.get())
        mommy.make(settings.AUTH_USER_MODEL, shortname='migrate_user')
        self.__create_period_permission_groups_in_default_database(
            subject_short_name='migrate_subject', period_short_name='migrate_period',
            permissiongroup_name='migrate_pmgroup')
        mommy.make('devilry_account.PermissionGroupUser',
                   user=get_user_model().objects.get(shortname='migrate_user'),
                   permissiongroup=account_models.PermissionGroup.objects.get(name='migrate_pmgroup'))

        # Migrate database data
        self.__create_period_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject', period_short_name='migrate_period',
            permissiongroup_name='migrate_pmgroup'
        )
        migrate_user = mommy.prepare(settings.AUTH_USER_MODEL, shortname='migrate_user')
        migrate_user.save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PermissionGroupUser',
                      user=migrate_user,
                      permissiongroup=account_models.PermissionGroup.objects.using(self.from_db_alias).get(
                          name='migrate_pmgroup')).save(using=self.from_db_alias)
        period_merger.PeriodPermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()

        # Control test, default user is still admin for default subject
        default_user = get_user_model().objects.get(shortname='default_user')
        period_queryset = core_models.Period.objects.filter_user_is_admin(user=default_user)
        self.assertEqual(period_queryset.count(), 1)
        self.assertEqual(period_queryset.get().short_name, 'default_period')

        # Migrate user is admin for migrate subject
        migrate_user = get_user_model().objects.get(shortname='migrate_user')
        period_queryset = core_models.Period.objects.filter_user_is_admin(user=migrate_user)
        self.assertEqual(period_queryset.count(), 1)
        self.assertEqual(period_queryset.get().short_name, 'migrate_period')
