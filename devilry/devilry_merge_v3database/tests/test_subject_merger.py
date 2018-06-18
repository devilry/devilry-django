from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import override_settings
from django.utils import timezone

from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_account import models as account_models
from devilry.devilry_merge_v3database.utils import subject_merger


class TestSubjectMerger(test.TestCase):
    from_db_alias = 'migrate_from'
    multi_db = True

    def test_databases_sanity(self):
        mommy.make('core.Subject', short_name='default_db_subject')
        mommy.prepare('core.Subject', short_name='migrate_db_subject').save(using=self.from_db_alias)

        # Test 'default' database.
        self.assertEqual(core_models.Subject.objects.count(), 1)
        self.assertEqual(core_models.Subject.objects.get().short_name, 'default_db_subject')

        # Test 'migrate_from' database.
        self.assertEqual(core_models.Subject.objects.using(self.from_db_alias).count(), 1)
        self.assertEqual(core_models.Subject.objects.using(self.from_db_alias).get().short_name, 'migrate_db_subject')

    def test_check_existing_subjects_not_affected(self):
        etag_datetime = timezone.now() - timezone.timedelta(days=50)
        mommy.make('core.Subject', short_name='default_db_subject', long_name='Default DB subject')
        mommy.prepare('core.Subject',
                      short_name='migrate_db_subject',
                      long_name='Migrate DB subject',
                      etag=etag_datetime)\
            .save(using=self.from_db_alias)

        subject_merger.SubjectMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        migrate_from_db_subject = core_models.Subject.objects.using(self.from_db_alias).get()
        migrated_subject = core_models.Subject.objects.get(short_name='migrate_db_subject')
        self.assertEqual(migrated_subject.long_name, migrate_from_db_subject.long_name)
        self.assertEqual(migrated_subject.etag, migrate_from_db_subject.etag)

        existing_default_subject = core_models.Subject.objects.get(short_name='default_db_subject')
        self.assertEqual(existing_default_subject.long_name, 'Default DB subject')

    def test_subject_is_migrated_sanity(self):
        mommy.make('core.Subject', short_name='default_db_subject')
        mommy.prepare('core.Subject', short_name='migrate_db_subject').save(using=self.from_db_alias)

        self.assertEqual(core_models.Subject.objects.count(), 1)
        self.assertEqual(core_models.Subject.objects.get().short_name, 'default_db_subject')
        subject_merger.SubjectMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.Subject.objects.count(), 2)
        self.assertTrue(core_models.Subject.objects.filter(short_name='migrate_db_subject').exists())

    def test_check_migrated_subject_fields(self):
        etag_datetime = timezone.now() - timezone.timedelta(days=50)
        mommy.prepare('core.Subject',
                      short_name='migrate_db_subject',
                      long_name='Migrate DB subject',
                      etag=etag_datetime)\
            .save(using=self.from_db_alias)

        subject_merger.SubjectMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        migrate_from_db_subject = core_models.Subject.objects.using(self.from_db_alias).get()
        migrated_subject = core_models.Subject.objects.get(short_name='migrate_db_subject')
        self.assertEqual(migrated_subject.long_name, migrate_from_db_subject.long_name)
        self.assertEqual(migrated_subject.etag, migrate_from_db_subject.etag)

    def test_multiple_subjects_migrated(self):
        mommy.prepare('core.Subject', short_name='migrate_db_subject1',
                      long_name='Migrate DB subject 1').save(using=self.from_db_alias)
        mommy.prepare('core.Subject', short_name='migrate_db_subject2',
                      long_name='Migrate DB subject 2').save(using=self.from_db_alias)
        mommy.prepare('core.Subject', short_name='migrate_db_subject3',
                      long_name='Migrate DB subject 3').save(using=self.from_db_alias)

        self.assertEqual(core_models.Subject.objects.count(), 0)
        subject_merger.SubjectMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.Subject.objects.count(), 3)

        self.assertEqual(core_models.Subject.objects.get(short_name='migrate_db_subject1').long_name,
                         'Migrate DB subject 1')
        self.assertEqual(core_models.Subject.objects.get(short_name='migrate_db_subject2').long_name,
                         'Migrate DB subject 2')
        self.assertEqual(core_models.Subject.objects.get(short_name='migrate_db_subject3').long_name,
                         'Migrate DB subject 3')


class TestSubjectPermissionGroupMerger(test.TestCase):
    from_db_alias = 'migrate_from'
    multi_db = True

    def __create_subject_permission_groups_in_default_database(self, subject_short_name, permissiongroup_name,
                                                               with_subject_permission_group=False):
        """
        Create Subject, PermissionGroup and SubjectPermissionGroup in default database.
        """
        pmgroup = mommy.make('devilry_account.PermissionGroup', name=permissiongroup_name,
                             grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        subject = mommy.make('core.Subject', short_name=subject_short_name)
        if with_subject_permission_group:
            mommy.make('devilry_account.SubjectPermissionGroup', subject=subject,
                       permissiongroup=pmgroup)

    def __create_subject_permission_groups_in_migrate_database(self, subject_short_name, permissiongroup_name):
        """
        Create Subject, PermissionGroup and SubjectPermissionGroup in database to migrate from.
        """
        pmgroup = mommy.prepare('devilry_account.PermissionGroup', name=permissiongroup_name,
                                        grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        pmgroup.save(using=self.from_db_alias)
        subject = mommy.prepare('core.Subject', short_name=subject_short_name)
        subject.save(using=self.from_db_alias)
        subject_pmgroup = mommy.prepare('devilry_account.SubjectPermissionGroup', subject=subject,
                                        permissiongroup=pmgroup)
        subject_pmgroup.save(using=self.from_db_alias)

    def test_database_sanity(self):
        # Default database data
        self.__create_subject_permission_groups_in_default_database(
            subject_short_name='default_subject', permissiongroup_name='default_pmgroup',
            with_subject_permission_group=True)

        # Migrate database data
        self.__create_subject_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject',
            permissiongroup_name='migrate_pmgroup')

        # Test default database
        self.assertEqual(account_models.PermissionGroup.objects.count(), 1)
        self.assertEqual(account_models.SubjectPermissionGroup.objects.count(), 1)
        self.assertEqual(core_models.Subject.objects.count(), 1)
        self.assertEqual(account_models.SubjectPermissionGroup.objects.get().permissiongroup.name, 'default_pmgroup')
        self.assertEqual(account_models.SubjectPermissionGroup.objects.get().subject.short_name, 'default_subject')

        # Test default database
        self.assertEqual(account_models.PermissionGroup.objects.using(self.from_db_alias).count(), 1)
        self.assertEqual(account_models.SubjectPermissionGroup.objects.using(self.from_db_alias).count(), 1)
        self.assertEqual(core_models.Subject.objects.using(self.from_db_alias).count(), 1)
        subjectpermission_group_queryset = account_models.SubjectPermissionGroup.objects.using(self.from_db_alias)
        self.assertEqual(subjectpermission_group_queryset.get().permissiongroup.name, 'migrate_pmgroup')
        self.assertEqual(subjectpermission_group_queryset.get().subject.short_name, 'migrate_subject')

    def test_check_existing_subject_permission_group_not_affected(self):
        # Default database data
        self.__create_subject_permission_groups_in_default_database(
            subject_short_name='default_subject', permissiongroup_name='default_pmgroup',
            with_subject_permission_group=True)
        self.__create_subject_permission_groups_in_default_database(
            subject_short_name='migrate_subject', permissiongroup_name='migrate_pmgroup')

        # Migrate database data
        self.__create_subject_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject',
            permissiongroup_name='migrate_pmgroup')

        self.assertEqual(account_models.SubjectPermissionGroup.objects.count(), 1)
        subject_merger.SubjectPermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(account_models.SubjectPermissionGroup.objects.count(), 2)
        default_subject_pmgroup = account_models.SubjectPermissionGroup.objects\
            .get(permissiongroup__name='default_pmgroup')
        self.assertEqual(default_subject_pmgroup.subject.short_name, 'default_subject')
        migrated_subject_pmgroup = account_models.SubjectPermissionGroup.objects\
            .get(permissiongroup__name='migrate_pmgroup')
        self.assertEqual(migrated_subject_pmgroup.subject.short_name, 'migrate_subject')

    def test_subject_and_permissiongroups_not_imported(self):
        self.__create_subject_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject',
            permissiongroup_name='migrate_pmgroup')
        with self.assertRaisesMessage(ValueError,
                                      'Subjects and PermissionGroups must be imported before SubjectPermissionGroups'):
            subject_merger.SubjectPermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_permissiongroups_not_imported(self):
        # Default database data
        mommy.make('core.Subject', short_name='migrate_subject')

        # Migrate database data
        self.__create_subject_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject',
            permissiongroup_name='migrate_pmgroup')

        with self.assertRaisesMessage(ValueError,
                                      'Subjects and PermissionGroups must be imported before SubjectPermissionGroups'):
            subject_merger.SubjectPermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_subjects_not_imported(self):
        # Default database data
        mommy.prepare('devilry_account.PermissionGroup', name='migrate_pmgroup',
                      grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)

        # Migrate database data
        self.__create_subject_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject',
            permissiongroup_name='migrate_pmgroup')

        with self.assertRaisesMessage(ValueError,
                                      'Subjects and PermissionGroups must be imported before SubjectPermissionGroups'):
            subject_merger.SubjectPermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_subject_permission_group_imported(self):
        # Default database data
        mommy.make('devilry_account.PermissionGroup', name='migrate_pmgroup',
                   grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        mommy.make('core.Subject', short_name='migrate_subject')

        # Migrate database data
        self.__create_subject_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject', permissiongroup_name='migrate_pmgroup')

        self.assertEqual(account_models.SubjectPermissionGroup.objects.count(), 0)
        subject_merger.SubjectPermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(account_models.SubjectPermissionGroup.objects.count(), 1)
        subject_permission_group = account_models.SubjectPermissionGroup.objects.get()
        self.assertEqual(subject_permission_group.subject.short_name, 'migrate_subject')
        self.assertEqual(subject_permission_group.permissiongroup.name, 'migrate_pmgroup')

    def test_multiple_subject_permission_groups_imported(self):
        # Default database data
        mommy.make('devilry_account.PermissionGroup', name='migrate_pmgroup1',
                   grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        mommy.make('core.Subject', short_name='migrate_subject1')
        mommy.make('devilry_account.PermissionGroup', name='migrate_pmgroup2',
                   grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        mommy.make('core.Subject', short_name='migrate_subject2')
        mommy.make('devilry_account.PermissionGroup', name='migrate_pmgroup3',
                   grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        mommy.make('core.Subject', short_name='migrate_subject3')

        # Migrate database data
        self.__create_subject_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject1', permissiongroup_name='migrate_pmgroup1')
        self.__create_subject_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject2', permissiongroup_name='migrate_pmgroup2')
        self.__create_subject_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject3', permissiongroup_name='migrate_pmgroup3')

        self.assertEqual(account_models.SubjectPermissionGroup.objects.count(), 0)
        subject_merger.SubjectPermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(account_models.SubjectPermissionGroup.objects.count(), 3)
        subject_pmgroup1 = account_models.SubjectPermissionGroup.objects.get(permissiongroup__name='migrate_pmgroup1')
        self.assertEqual(subject_pmgroup1.subject.short_name, 'migrate_subject1')
        subject_pmgroup2 = account_models.SubjectPermissionGroup.objects.get(permissiongroup__name='migrate_pmgroup2')
        self.assertEqual(subject_pmgroup2.subject.short_name, 'migrate_subject2')
        subject_pmgroup3 = account_models.SubjectPermissionGroup.objects.get(permissiongroup__name='migrate_pmgroup3')
        self.assertEqual(subject_pmgroup3.subject.short_name, 'migrate_subject3')

    def test_subject_permission_groups_on_same_subject_raises_validation_error(self):
        # Default database data
        self.__create_subject_permission_groups_in_default_database(
            subject_short_name='subject', permissiongroup_name='pmgroup', with_subject_permission_group=True)

        # Migrate database data
        self.__create_subject_permission_groups_in_migrate_database(
            subject_short_name='subject', permissiongroup_name='pmgroup')
        with self.assertRaises(ValidationError):
            subject_merger.SubjectPermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_migrated_user_is_admin_on_subject_after_import(self):
        # Default database data
        self.__create_subject_permission_groups_in_default_database(
            subject_short_name='default_subject', permissiongroup_name='default_pmgroup',
            with_subject_permission_group=True)
        default_user = mommy.make(settings.AUTH_USER_MODEL, shortname='default_user')
        mommy.make('devilry_account.PermissionGroupUser', user=default_user,
                   permissiongroup=account_models.PermissionGroup.objects.get())
        mommy.make(settings.AUTH_USER_MODEL, shortname='migrate_user')
        self.__create_subject_permission_groups_in_default_database(
            subject_short_name='migrate_subject', permissiongroup_name='migrate_pmgroup')
        mommy.make('devilry_account.PermissionGroupUser',
                   user=get_user_model().objects.get(shortname='migrate_user'),
                   permissiongroup=account_models.PermissionGroup.objects.get(name='migrate_pmgroup'))

        # Migrate database data
        self.__create_subject_permission_groups_in_migrate_database(
            subject_short_name='migrate_subject', permissiongroup_name='migrate_pmgroup'
        )
        migrate_user = mommy.prepare(settings.AUTH_USER_MODEL, shortname='migrate_user')
        migrate_user.save(using=self.from_db_alias)
        mommy.prepare('devilry_account.PermissionGroupUser',
                      user=migrate_user,
                      permissiongroup=account_models.PermissionGroup.objects.using(self.from_db_alias).get(
                          name='migrate_pmgroup')).save(using=self.from_db_alias)

        subject_merger.SubjectPermissionGroupMerger(from_db_alias=self.from_db_alias, transaction=True).run()

        # Control test, default user is still admin for default subject
        default_user = get_user_model().objects.get(shortname='default_user')
        subject_queryset = core_models.Subject.objects.filter_user_is_admin(user=default_user)
        self.assertEqual(subject_queryset.count(), 1)
        self.assertEqual(subject_queryset.get().short_name, 'default_subject')

        # Migrate user is admin for migrate subject
        migrate_user = get_user_model().objects.get(shortname='migrate_user')
        subject_queryset = core_models.Subject.objects.filter_user_is_admin(user=migrate_user)
        self.assertEqual(subject_queryset.count(), 1)
        self.assertEqual(subject_queryset.get().short_name, 'migrate_subject')


