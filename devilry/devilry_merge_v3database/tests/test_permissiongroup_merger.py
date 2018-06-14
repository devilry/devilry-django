from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import override_settings
from django.utils import timezone

from model_mommy import mommy

from devilry.devilry_account import models as account_models
from devilry.apps.core import models as core_models
from devilry.devilry_merge_v3database.utils import permissiongroup_merger


class TestPermissionGroupMerger(test.TestCase):
    from_db_alias = 'migrate_from'
    multi_db = True

    def test_database_sanity(self):
        # Default database data
        mommy.make('devilry_account.PermissionGroup', name='default_pm')

        # Migrate database data
        mommy.prepare('devilry_account.PermissionGroup', name='migrate_pm').save(using=self.from_db_alias)

        # Test default database
        self.assertEqual(account_models.PermissionGroup.objects.count(), 1)
        self.assertEqual(account_models.PermissionGroup.objects.get().name, 'default_pm')

        # Test migrate database
        self.assertEqual(account_models.PermissionGroup.objects.using(self.from_db_alias).count(), 1)
        self.assertEqual(account_models.PermissionGroup.objects.using(self.from_db_alias).get().name, 'migrate_pm')

    def test_check_existing_permissiongroup_not_affected(self):
        default_syncsystem_update_datetime = timezone.now()
        migrate_syncsystem_update_datetime = timezone.now() - timezone.timedelta(days=10)
        mommy.make('devilry_account.PermissionGroup',
                   name='default_pm',
                   syncsystem_update_datetime=default_syncsystem_update_datetime,
                   grouptype=account_models.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
        mommy.prepare('devilry_account.PermissionGroup',
                      name='migrate_pm',
                      syncsystem_update_datetime=migrate_syncsystem_update_datetime,
                      grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                      is_custom_manageable=True).save(using=self.from_db_alias)
        permissiongroup_merger.PermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()

        self.assertEqual(account_models.PermissionGroup.objects.count(), 2)
        default_permissiongroup = account_models.PermissionGroup.objects.get(name='default_pm')
        self.assertEqual(default_permissiongroup.grouptype, account_models.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
        self.assertEqual(default_permissiongroup.syncsystem_update_datetime, default_syncsystem_update_datetime)
        self.assertFalse(default_permissiongroup.is_custom_manageable)

    def test_permission_group_migrate_sanity(self):
        created_datetime = timezone.now() - timezone.timedelta(days=30)
        updated_datetime = timezone.now() - timezone.timedelta(days=20)
        syncsystem_update_datetime = timezone.now() - timezone.timedelta(days=10)
        mommy.prepare('devilry_account.PermissionGroup',
                      name='migrate_pm',
                      grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN,
                      is_custom_manageable=True).save(using=self.from_db_alias)
        account_models.PermissionGroup.objects.using(self.from_db_alias).filter(name='migrate_pm').update(
            created_datetime=created_datetime,
            updated_datetime=updated_datetime,
            syncsystem_update_datetime=syncsystem_update_datetime
        )

        self.assertEqual(account_models.PermissionGroup.objects.count(), 0)
        permissiongroup_merger.PermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()

        self.assertEqual(account_models.PermissionGroup.objects.count(), 1)
        migrate_permissiongroup = account_models.PermissionGroup.objects.get(name='migrate_pm')
        self.assertEqual(migrate_permissiongroup.grouptype, account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        self.assertEqual(migrate_permissiongroup.created_datetime, created_datetime)
        self.assertEqual(migrate_permissiongroup.updated_datetime, updated_datetime)
        self.assertEqual(migrate_permissiongroup.syncsystem_update_datetime, syncsystem_update_datetime)
        self.assertTrue(migrate_permissiongroup.is_custom_manageable)

    def test_multiple_permission_groups_migrated_sanity(self):
        mommy.prepare('devilry_account.PermissionGroup',
                      name='migrate_pm_type_department',
                      grouptype=account_models.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN).save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PermissionGroup',
                      name='migrate_pm_type_subject',
                      grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN).save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PermissionGroup',
                      name='migrate_pm_type_period',
                      grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN).save(using=self.from_db_alias)
        self.assertEqual(account_models.PermissionGroup.objects.count(), 0)
        permissiongroup_merger.PermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(account_models.PermissionGroup.objects.count(), 3)
        self.assertEqual(account_models.PermissionGroup.objects.filter(name='migrate_pm_type_department').count(), 1)
        self.assertEqual(account_models.PermissionGroup.objects.filter(name='migrate_pm_type_subject').count(), 1)
        self.assertEqual(account_models.PermissionGroup.objects.filter(name='migrate_pm_type_period').count(), 1)

    def test_multiple_permission_groups_migrated_with_existing_permission_groups_sanity(self):
        # Default database data
        mommy.make('devilry_account.PermissionGroup',
                      name='default_pm_type_department',
                      grouptype=account_models.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
        mommy.make('devilry_account.PermissionGroup',
                      name='default_pm_type_subject',
                      grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        mommy.make('devilry_account.PermissionGroup',
                      name='default_pm_type_period',
                      grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN)

        # Migrate database data
        mommy.prepare('devilry_account.PermissionGroup',
                      name='migrate_pm_type_department',
                      grouptype=account_models.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN).save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PermissionGroup',
                      name='migrate_pm_type_subject',
                      grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN).save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PermissionGroup',
                      name='migrate_pm_type_period',
                      grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN).save(using=self.from_db_alias)

        self.assertEqual(account_models.PermissionGroup.objects.count(), 3)
        permissiongroup_merger.PermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(account_models.PermissionGroup.objects.count(), 6)
        self.assertEqual(account_models.PermissionGroup.objects.filter(name='default_pm_type_department').count(), 1)
        self.assertEqual(account_models.PermissionGroup.objects.filter(name='default_pm_type_subject').count(), 1)
        self.assertEqual(account_models.PermissionGroup.objects.filter(name='default_pm_type_period').count(), 1)
        self.assertEqual(account_models.PermissionGroup.objects.filter(name='migrate_pm_type_department').count(), 1)
        self.assertEqual(account_models.PermissionGroup.objects.filter(name='migrate_pm_type_subject').count(), 1)
        self.assertEqual(account_models.PermissionGroup.objects.filter(name='migrate_pm_type_period').count(), 1)

    def test_permission_group_with_name_exists_in_default_database(self):
        mommy.make('devilry_account.PermissionGroup', name='pm')
        mommy.prepare('devilry_account.PermissionGroup', name='pm').save(using=self.from_db_alias)
        with self.assertRaises(ValidationError):
            permissiongroup_merger.PermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(account_models.PermissionGroup.objects.count(), 1)

    def test_permission_group_is_saved_with_another_id_sanity(self):
        mommy.make('devilry_account.PermissionGroup', name='default_pm')
        mommy.prepare('devilry_account.PermissionGroup', name='migrate_pm').save(using=self.from_db_alias)
        self.assertEqual(account_models.PermissionGroup.objects.get().name, 'default_pm')
        self.assertEqual(account_models.PermissionGroup.objects.using(self.from_db_alias).get().name, 'migrate_pm')

        permissiongroup_merger.PermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()

        self.assertEqual(account_models.PermissionGroup.objects.count(), 2)
        self.assertNotEqual(account_models.PermissionGroup.objects.first().id,
                            account_models.PermissionGroup.objects.last().id)
        self.assertNotEqual(account_models.PermissionGroup.objects.first().name,
                            account_models.PermissionGroup.objects.last().name)


class TestPermissionGroupUserMerger(test.TestCase):
    from_db_alias = 'migrate_from'
    multi_db = True

    def test_database_sanity(self):
        # Default database data
        default_user = mommy.make(settings.AUTH_USER_MODEL, shortname='default_user')
        default_pm = mommy.make('devilry_account.PermissionGroup', name='default_pm')
        mommy.make('devilry_account.PermissionGroupUser', user=default_user, permissiongroup=default_pm)

        # Migrate database data
        migrate_user = mommy.prepare(settings.AUTH_USER_MODEL, shortname='migrate_user')
        migrate_user.save(using=self.from_db_alias)
        migrate_pm = mommy.prepare('devilry_account.PermissionGroup', name='migrate_pm')
        migrate_pm.save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PermissionGroupUser', user=migrate_user, permissiongroup=migrate_pm)\
            .save(using=self.from_db_alias)

        # Test default database
        self.assertEqual(account_models.PermissionGroupUser.objects.count(), 1)
        self.assertEqual(account_models.PermissionGroupUser.objects.get().user.shortname, 'default_user')
        self.assertEqual(account_models.PermissionGroupUser.objects.get().permissiongroup.name, 'default_pm')

        # Test migrate database
        permissiongroupuser_queryset = account_models.PermissionGroupUser.objects\
            .using(self.from_db_alias)\
            .select_related('user', 'permissiongroup')
        self.assertEqual(permissiongroupuser_queryset.count(), 1)
        self.assertEqual(permissiongroupuser_queryset.get().user.shortname,
                         'migrate_user')
        self.assertEqual(permissiongroupuser_queryset.get().permissiongroup.name,
                         'migrate_pm')

    def test_permissiongroup_and_user_not_imported(self):
        # Migrate database data
        migrate_pm = mommy.prepare('devilry_account.PermissionGroup', name='migrate_pm')
        migrate_pm.save(using=self.from_db_alias)
        migrate_user = mommy.prepare(settings.AUTH_USER_MODEL)
        migrate_user.save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PermissionGroupUser', user=migrate_user, permissiongroup=migrate_pm)\
            .save(using=self.from_db_alias)

        with self.assertRaisesMessage(
                ValueError, 'PermissionGroups and Users must be imported before PermissionGroupUser'):
            permissiongroup_merger.PermissionGroupUserMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_permissiongroup_not_imported(self):
        # Default database data
        mommy.make(settings.AUTH_USER_MODEL, shortname='migrate_user')

        # Migrate database data
        migrate_pm = mommy.prepare('devilry_account.PermissionGroup', name='migrate_pm')
        migrate_pm.save(using=self.from_db_alias)
        migrate_user = mommy.prepare(settings.AUTH_USER_MODEL, shortname='migrate_user')
        migrate_user.save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PermissionGroupUser', user=migrate_user, permissiongroup=migrate_pm)\
            .save(using=self.from_db_alias)

        with self.assertRaisesMessage(
                ValueError, 'PermissionGroups and Users must be imported before PermissionGroupUser'):
            permissiongroup_merger.PermissionGroupUserMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_user_not_imported(self):
        # Default database data
        mommy.make('devilry_account.PermissionGroup', name='migrate_pm')

        # Migrate database data
        migrate_pm = mommy.prepare('devilry_account.PermissionGroup', name='migrate_pm')
        migrate_pm.save(using=self.from_db_alias)
        migrate_user = mommy.prepare(settings.AUTH_USER_MODEL, shortname='migrate_user')
        migrate_user.save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PermissionGroupUser', user=migrate_user, permissiongroup=migrate_pm)\
            .save(using=self.from_db_alias)

        with self.assertRaisesMessage(
                ValueError, 'PermissionGroups and Users must be imported before PermissionGroupUser'):
            permissiongroup_merger.PermissionGroupUserMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_permission_group_user_is_migrated_sanity(self):
        # Default database data
        migrated_user = mommy.make(settings.AUTH_USER_MODEL, shortname='migrate_user')
        mommy.make('devilry_account.PermissionGroup', name='migrate_pm')

        # Migrate database data
        migrate_pm = mommy.prepare('devilry_account.PermissionGroup', name='migrate_pm')
        migrate_pm.save(using=self.from_db_alias)
        migrate_user = mommy.prepare(settings.AUTH_USER_MODEL, shortname='migrate_user')
        migrate_user.save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PermissionGroupUser', user=migrate_user, permissiongroup=migrate_pm) \
            .save(using=self.from_db_alias)

        self.assertEqual(account_models.PermissionGroupUser.objects.count(), 0)
        permissiongroup_merger.PermissionGroupUserMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(account_models.PermissionGroupUser.objects.count(), 1)
        self.assertEqual(account_models.PermissionGroupUser.objects.get().user.shortname, migrated_user.shortname)
        self.assertEqual(account_models.PermissionGroupUser.objects.get().permissiongroup.name, migrate_pm.name)

    def test_multiple_permission_group_users_migrated_sanity(self):
        # Default database data
        migrated_user1 = mommy.make(settings.AUTH_USER_MODEL, shortname='migrate_user1')
        mommy.make('devilry_account.PermissionGroup', name='migrate_pm1',
                   grouptype=account_models.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)

        migrated_user2 = mommy.make(settings.AUTH_USER_MODEL, shortname='migrate_user2')
        mommy.make('devilry_account.PermissionGroup', name='migrate_pm2',
                   grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)

        migrated_user3 = mommy.make(settings.AUTH_USER_MODEL, shortname='migrate_user3')
        mommy.make('devilry_account.PermissionGroup', name='migrate_pm3',
                   grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN)

        # Migrate database data
        migrate_pm1 = mommy.prepare('devilry_account.PermissionGroup', name='migrate_pm1',
                                    grouptype=account_models.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
        migrate_pm1.save(using=self.from_db_alias)
        migrate_user1 = mommy.prepare(settings.AUTH_USER_MODEL, shortname='migrate_user1')
        migrate_user1.save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PermissionGroupUser', user=migrate_user1, permissiongroup=migrate_pm1) \
            .save(using=self.from_db_alias)

        migrate_pm2 = mommy.prepare('devilry_account.PermissionGroup', name='migrate_pm2',
                                    grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        migrate_pm2.save(using=self.from_db_alias)
        migrate_user2 = mommy.prepare(settings.AUTH_USER_MODEL, shortname='migrate_user2')
        migrate_user2.save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PermissionGroupUser', user=migrate_user2, permissiongroup=migrate_pm2) \
            .save(using=self.from_db_alias)

        migrate_pm3 = mommy.prepare('devilry_account.PermissionGroup', name='migrate_pm3',
                                    grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN)
        migrate_pm3.save(using=self.from_db_alias)
        migrate_user3 = mommy.prepare(settings.AUTH_USER_MODEL, shortname='migrate_user3')
        migrate_user3.save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PermissionGroupUser', user=migrate_user3, permissiongroup=migrate_pm3) \
            .save(using=self.from_db_alias)

        self.assertEqual(account_models.PermissionGroupUser.objects.count(), 0)
        permissiongroup_merger.PermissionGroupUserMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        permissiongroupuser_queryset = account_models.PermissionGroupUser.objects
        self.assertEqual(permissiongroupuser_queryset.count(), 3)

        # Test PermissionGroupUser migrated for migrated_user1
        self.assertEqual(
            permissiongroupuser_queryset.filter(permissiongroup__name='migrate_pm1').get().user.shortname,
            migrated_user1.shortname
        )
        self.assertEqual(
            permissiongroupuser_queryset.filter(permissiongroup__name='migrate_pm1').get().permissiongroup.name,
            migrate_pm1.name
        )
        self.assertEqual(
            permissiongroupuser_queryset.filter(permissiongroup__name='migrate_pm1').get().permissiongroup.grouptype,
            account_models.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN
        )

        # Test PermissionGroupUser migrated for migrated_user2
        self.assertEqual(
            permissiongroupuser_queryset.filter(permissiongroup__name='migrate_pm2').get().user.shortname,
            migrated_user2.shortname
        )
        self.assertEqual(
            permissiongroupuser_queryset.filter(permissiongroup__name='migrate_pm2').get().permissiongroup.name,
            migrate_pm2.name
        )
        self.assertEqual(
            permissiongroupuser_queryset.filter(permissiongroup__name='migrate_pm2').get().permissiongroup.grouptype,
            account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN
        )

        # Test PermissionGroupUser migrated for migrated_user3
        self.assertEqual(
            permissiongroupuser_queryset.filter(permissiongroup__name='migrate_pm3').get().user.shortname,
            migrated_user3.shortname
        )
        self.assertEqual(
            permissiongroupuser_queryset.filter(permissiongroup__name='migrate_pm3').get().permissiongroup.name,
            migrate_pm3.name
        )
        self.assertEqual(
            permissiongroupuser_queryset.filter(permissiongroup__name='migrate_pm3').get().permissiongroup.grouptype,
            account_models.PermissionGroup.GROUPTYPE_PERIODADMIN
        )

    def test_user_in_multiple_migrate_permission_group_users(self):
        # Default database data
        migrated_user = mommy.make(settings.AUTH_USER_MODEL, shortname='migrate_user')
        mommy.make('devilry_account.PermissionGroup', name='migrate_pm1',
                   grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        mommy.make('devilry_account.PermissionGroup', name='migrate_pm2',
                   grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        mommy.make('devilry_account.PermissionGroup', name='migrate_pm3',
                   grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)

        # Migrate database data
        migrate_user = mommy.prepare(settings.AUTH_USER_MODEL, shortname='migrate_user')
        migrate_user.save(using=self.from_db_alias)
        migrate_pm1 = mommy.prepare('devilry_account.PermissionGroup', name='migrate_pm1',
                                    grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        migrate_pm1.save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PermissionGroupUser', user=migrate_user, permissiongroup=migrate_pm1)\
            .save(using=self.from_db_alias)
        migrate_pm2 = mommy.prepare('devilry_account.PermissionGroup', name='migrate_pm2',
                                    grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        migrate_pm2.save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PermissionGroupUser', user=migrate_user, permissiongroup=migrate_pm2)\
            .save(using=self.from_db_alias)
        migrate_pm3 = mommy.prepare('devilry_account.PermissionGroup', name='migrate_pm3',
                                    grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        migrate_pm3.save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PermissionGroupUser', user=migrate_user, permissiongroup=migrate_pm3)\
            .save(using=self.from_db_alias)

        self.assertEqual(account_models.PermissionGroupUser.objects.count(), 0)
        permissiongroup_merger.PermissionGroupUserMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(account_models.PermissionGroupUser.objects.count(), 3)
        permissiongroupuser_queryset = account_models.PermissionGroupUser.objects
        self.assertEqual(permissiongroupuser_queryset.filter(permissiongroup__name='migrate_pm1').get().user.shortname,
                         'migrate_user')
        self.assertEqual(permissiongroupuser_queryset.filter(permissiongroup__name='migrate_pm2').get().user.shortname,
                         'migrate_user')
        self.assertEqual(permissiongroupuser_queryset.filter(permissiongroup__name='migrate_pm3').get().user.shortname,
                         'migrate_user')

    def __create_permission_group_and_user_default_db(self, user_shortname, permissiongroup_name,
                                                      grouptype, with_permissiongroup_user=False):
        """
        Helper method for creating PermissionGroup with or without PermissionGroupUser in the default database.
        """
        pm = mommy.make('devilry_account.PermissionGroup', name=permissiongroup_name, grouptype=grouptype)
        user = mommy.make(settings.AUTH_USER_MODEL, shortname=user_shortname)
        if with_permissiongroup_user:
            mommy.make('devilry_account.PermissionGroupUser', user=user, permissiongroup=pm)

    def __create_permission_group_and_user_migrate_from_db(self, user_shortname, permissiongroup_name,
                                                           grouptype, with_permissiongroup_user=False):
        """
        Helper method for creating PermissionGroup with or without PermissionGroupUser in the migrate from database.
        """
        user = mommy.prepare(settings.AUTH_USER_MODEL, shortname=user_shortname)
        user.save(using=self.from_db_alias)
        pm = mommy.prepare('devilry_account.PermissionGroup', name=permissiongroup_name, grouptype=grouptype)
        pm.save(using=self.from_db_alias)
        if with_permissiongroup_user:
            mommy.prepare('devilry_account.PermissionGroupUser', user=user, permissiongroup=pm)\
                .save(using=self.from_db_alias)

    def test_multiple_permission_group_users_migrated_with_existing_permission_group_users_sanity(self):
        # Default database data
        self.__create_permission_group_and_user_default_db(
            user_shortname='default_user1', permissiongroup_name='default_pm_type_department',
            grouptype=account_models.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN, with_permissiongroup_user=True)
        self.__create_permission_group_and_user_default_db(
            user_shortname='default_user2', permissiongroup_name='default_pm_type_subject',
            grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN, with_permissiongroup_user=True)
        self.__create_permission_group_and_user_default_db(
            user_shortname='default_user3', permissiongroup_name='default_pm_type_period',
            grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN, with_permissiongroup_user=True)

        self.__create_permission_group_and_user_default_db(
            user_shortname='migrate_user1', permissiongroup_name='migrate_pm_type_department',
            grouptype=account_models.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
        self.__create_permission_group_and_user_default_db(
            user_shortname='migrate_user2', permissiongroup_name='migrate_pm_type_subject',
            grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        self.__create_permission_group_and_user_default_db(
            user_shortname='migrate_user3', permissiongroup_name='migrate_pm_type_period',
            grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN)

        # Migrate database data
        self.__create_permission_group_and_user_migrate_from_db(
            user_shortname='migrate_user1', permissiongroup_name='migrate_pm_type_department',
            grouptype=account_models.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN, with_permissiongroup_user=True)
        self.__create_permission_group_and_user_migrate_from_db(
            user_shortname='migrate_user2', permissiongroup_name='migrate_pm_type_subject',
            grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN, with_permissiongroup_user=True)
        self.__create_permission_group_and_user_migrate_from_db(
            user_shortname='migrate_user3', permissiongroup_name='migrate_pm_type_period',
            grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN, with_permissiongroup_user=True)

        self.assertEqual(get_user_model().objects.count(), 6)
        self.assertEqual(account_models.PermissionGroup.objects.count(), 6)
        self.assertEqual(account_models.PermissionGroupUser.objects.count(), 3)

        permissiongroup_merger.PermissionGroupUserMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(get_user_model().objects.count(), 6)
        self.assertEqual(account_models.PermissionGroup.objects.count(), 6)
        self.assertEqual(account_models.PermissionGroupUser.objects.count(), 6)
        pm_user_queryset = account_models.PermissionGroupUser.objects
        self.assertEqual(
            pm_user_queryset.filter(
                permissiongroup__name='default_pm_type_department',
                permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
                .get().user.shortname,
            'default_user1')
        self.assertEqual(
            pm_user_queryset.filter(
                permissiongroup__name='default_pm_type_subject',
                permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)
                .get().user.shortname,
            'default_user2')
        self.assertEqual(
            pm_user_queryset.filter(
                permissiongroup__name='default_pm_type_period',
                permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN)
                .get().user.shortname,
            'default_user3')

        self.assertEqual(
            pm_user_queryset.filter(
                permissiongroup__name='migrate_pm_type_department',
                permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
                .get().user.shortname,
            'migrate_user1')
        self.assertEqual(
            pm_user_queryset.filter(
                permissiongroup__name='migrate_pm_type_subject',
                permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)
                .get().user.shortname,
            'migrate_user2')
        self.assertEqual(
            pm_user_queryset.filter(
                permissiongroup__name='migrate_pm_type_period',
                permissiongroup__grouptype=account_models.PermissionGroup.GROUPTYPE_PERIODADMIN)
                .get().user.shortname,
            'migrate_user3')
