from django import test
from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import override_settings
from django.utils import timezone

from model_mommy import mommy

from devilry.apps.core import models as core_models
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

    def test_raises_error_when_subject_shortname_in_migrate_db_exists_in_default_db(self):
        mommy.make('core.Subject', short_name='subject', long_name='Default DB subject')
        mommy.prepare('core.Subject', short_name='subject').save(using=self.from_db_alias)
        with self.assertRaises(ValidationError):
            subject_merger.SubjectMerger(from_db_alias=self.from_db_alias, transaction=True).run()

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
    """
    """
    def test_sanity(self):
        pass
