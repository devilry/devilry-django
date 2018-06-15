from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import override_settings
from django.utils import timezone

from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_account import models as account_models
from devilry.devilry_merge_v3database.utils import relateduser_merger


class TestRelatedExaminerMerger(test.TestCase):
    from_db_alias = 'migrate_from'
    multi_db = True

    def __create_for_default_db(self, user_shortname, subject_short_name, period_short_name,
                                with_related_examiner=False, related_examiner_kwargs=None):
        subject = mommy.make('core.Subject', short_name=subject_short_name)
        period = mommy.make('core.Period', short_name=period_short_name, parentnode=subject)
        user = mommy.make(settings.AUTH_USER_MODEL, shortname=user_shortname)
        if with_related_examiner:
            if related_examiner_kwargs:
                mommy.make('core.RelatedExaminer', user=user, period=period, **related_examiner_kwargs)
            else:
                mommy.make('core.RelatedExaminer', user=user, period=period)

    def __create_for_migrate_db(self, user_shortname, subject_short_name, period_short_name,
                                related_examiner_kwargs=None):
        subject = mommy.prepare('core.Subject', short_name=subject_short_name)
        subject.save(using=self.from_db_alias)
        period = mommy.prepare('core.Period', short_name=period_short_name, parentnode=subject)
        period.save(using=self.from_db_alias)
        user = mommy.prepare(settings.AUTH_USER_MODEL, shortname=user_shortname)
        user.save(using=self.from_db_alias)
        if related_examiner_kwargs:
            mommy.prepare('core.RelatedExaminer', user=user, period=period, **related_examiner_kwargs)\
                .save(using=self.from_db_alias)
        else:
            mommy.prepare('core.RelatedExaminer', user=user, period=period).save(using=self.from_db_alias)

    def test_databases_sanity(self):
        # Default database data
        self.__create_for_default_db(user_shortname='default_user', subject_short_name='default_subject',
                                     period_short_name='default_period', with_related_examiner=True)

        # Migrate database data
        self.__create_for_migrate_db(user_shortname='migrate_user', subject_short_name='migrate_subject',
                                     period_short_name='migrate_period')

        # Test 'default' database.
        self.assertEqual(core_models.RelatedExaminer.objects.count(), 1)
        self.assertEqual(core_models.RelatedExaminer.objects.get().user.shortname, 'default_user')
        self.assertEqual(core_models.RelatedExaminer.objects.get().period.parentnode.short_name, 'default_subject')
        self.assertEqual(core_models.RelatedExaminer.objects.get().period.short_name, 'default_period')

        # Test 'migrate_from' database.
        self.assertEqual(core_models.RelatedExaminer.objects.using(self.from_db_alias).count(), 1)
        related_examiner_migratedb_queryset = core_models.RelatedExaminer.objects\
            .using(self.from_db_alias)\
            .select_related('user', 'period', 'period__parentnode')
        self.assertEqual(
            related_examiner_migratedb_queryset.get().user.shortname,
            'migrate_user')
        self.assertEqual(
            related_examiner_migratedb_queryset.get().period.parentnode.short_name,
            'migrate_subject')
        self.assertEqual(
            related_examiner_migratedb_queryset.get().period.short_name,
            'migrate_period')

    def test_user_period_subject_not_imported(self):
        self.__create_for_migrate_db(user_shortname='migrate_user', subject_short_name='migrate_subject',
                                     period_short_name='migrate_period')
        with self.assertRaisesMessage(ValueError,
                                      'Users, Subjects and Periods must be imported before RelatedExaminers'):
            relateduser_merger.RelatedExaminerMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_user_period_not_imported(self):
        # Default database data
        mommy.make('core.Subject', short_name='migrate_subject')

        # Migrate database data
        self.__create_for_migrate_db(user_shortname='migrate_user', subject_short_name='migrate_subject',
                                     period_short_name='migrate_period')
        with self.assertRaisesMessage(ValueError,
                                      'Users, Subjects and Periods must be imported before RelatedExaminers'):
            relateduser_merger.RelatedExaminerMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_user_not_imported(self):
        # Default database data
        subject = mommy.make('core.Subject', short_name='migrate_subject')
        mommy.make('core.Period', short_name='migrate_period', parentnode=subject)

        # Migrate database data
        self.__create_for_migrate_db(user_shortname='migrate_user', subject_short_name='migrate_subject',
                                     period_short_name='migrate_period')
        with self.assertRaisesMessage(ValueError,
                                      'Users, Subjects and Periods must be imported before RelatedExaminers'):
            relateduser_merger.RelatedExaminerMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_related_examiner_imported_sanity(self):
        # Default database data
        default_db_subject = mommy.make('core.Subject', id=105, short_name='migrate_subject')
        default_db_period = mommy.make('core.Period', id=105, short_name='migrate_period',
                                       parentnode=default_db_subject)
        default_db_user = mommy.make(settings.AUTH_USER_MODEL, id=105, shortname='migrate_user')

        # Migrate database data
        self.__create_for_migrate_db(user_shortname='migrate_user', subject_short_name='migrate_subject',
                                     period_short_name='migrate_period')
        self.assertEqual(core_models.RelatedExaminer.objects.count(), 0)
        relateduser_merger.RelatedExaminerMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.RelatedExaminer.objects.count(), 1)
        self.assertEqual(core_models.RelatedExaminer.objects.get().user, default_db_user)
        self.assertEqual(core_models.RelatedExaminer.objects.get().user.shortname, 'migrate_user')
        self.assertEqual(core_models.RelatedExaminer.objects.get().period, default_db_period)
        self.assertEqual(core_models.RelatedExaminer.objects.get().period.short_name, 'migrate_period')
        self.assertEqual(core_models.RelatedExaminer.objects.get().period.parentnode, default_db_subject)
        self.assertEqual(core_models.RelatedExaminer.objects.get().period.parentnode.short_name, 'migrate_subject')

    def test_import_does_not_affect_existing_related_examiner(self):
        # Default database data
        default_relatedexaminer_kwargs = {
            'automatic_anonymous_id': 'd_aaID',
            'tags': 'd_tag1,d_tag2,d_tag3'
        }
        self.__create_for_default_db(user_shortname='default_user', subject_short_name='default_subject',
                                     period_short_name='default_period', with_related_examiner=True,
                                     related_examiner_kwargs=default_relatedexaminer_kwargs)
        self.__create_for_default_db(user_shortname='migrate_user', subject_short_name='migrate_subject',
                                     period_short_name='migrate_period')

        # Migrate database data
        migrate_relatedexaminer_kwargs = {
            'automatic_anonymous_id': 'm_aaID',
            'tags': 'm_tag1,m_tag2,m_tag3'
        }
        self.__create_for_migrate_db(user_shortname='migrate_user', subject_short_name='migrate_subject',
                                     period_short_name='migrate_period',
                                     related_examiner_kwargs=migrate_relatedexaminer_kwargs)

        relateduser_merger.RelatedExaminerMerger(from_db_alias=self.from_db_alias, transaction=True).run()

        # Test existing RelatedStudent
        default_related_examiner = core_models.RelatedExaminer.objects.get(user__shortname='default_user')
        self.assertEqual(default_related_examiner.automatic_anonymous_id, 'd_aaID')
        self.assertEqual(default_related_examiner.tags, 'd_tag1,d_tag2,d_tag3')

        # Test migrated RelatedStudent
        migrated_related_examiner = core_models.RelatedExaminer.objects.get(user__shortname='migrate_user')
        self.assertEqual(migrated_related_examiner.automatic_anonymous_id, 'm_aaID')
        self.assertEqual(migrated_related_examiner.tags, 'm_tag1,m_tag2,m_tag3')


class TestRelatedStudentMerger(test.TestCase):
    from_db_alias = 'migrate_from'
    multi_db = True

    def __create_for_default_db(self, user_shortname, subject_short_name, period_short_name,
                                with_related_student=False, related_student_kwargs=None):
        subject = mommy.make('core.Subject', short_name=subject_short_name)
        period = mommy.make('core.Period', short_name=period_short_name, parentnode=subject)
        user = mommy.make(settings.AUTH_USER_MODEL, shortname=user_shortname)
        if with_related_student:
            if related_student_kwargs:
                mommy.make('core.RelatedStudent', user=user, period=period, **related_student_kwargs)
            else:
                mommy.make('core.RelatedStudent', user=user, period=period)

    def __create_for_migrate_db(self, user_shortname, subject_short_name, period_short_name,
                                related_student_kwargs=None):
        subject = mommy.prepare('core.Subject', short_name=subject_short_name)
        subject.save(using=self.from_db_alias)
        period = mommy.prepare('core.Period', short_name=period_short_name, parentnode=subject)
        period.save(using=self.from_db_alias)
        user = mommy.prepare(settings.AUTH_USER_MODEL, shortname=user_shortname)
        user.save(using=self.from_db_alias)
        if related_student_kwargs:
            mommy.prepare('core.RelatedStudent', user=user, period=period, **related_student_kwargs)\
                .save(using=self.from_db_alias)
        else:
            mommy.prepare('core.RelatedStudent', user=user, period=period).save(using=self.from_db_alias)

    def test_databases_sanity(self):
        # Default database data
        self.__create_for_default_db(user_shortname='default_user', subject_short_name='default_subject',
                                     period_short_name='default_period', with_related_student=True)

        # Migrate database data
        self.__create_for_migrate_db(user_shortname='migrate_user', subject_short_name='migrate_subject',
                                     period_short_name='migrate_period')

        # Test 'default' database.
        self.assertEqual(core_models.RelatedStudent.objects.count(), 1)
        self.assertEqual(core_models.RelatedStudent.objects.get().user.shortname, 'default_user')
        self.assertEqual(core_models.RelatedStudent.objects.get().period.parentnode.short_name, 'default_subject')
        self.assertEqual(core_models.RelatedStudent.objects.get().period.short_name, 'default_period')

        # Test 'migrate_from' database.
        self.assertEqual(core_models.RelatedStudent.objects.using(self.from_db_alias).count(), 1)
        related_examiner_migratedb_queryset = core_models.RelatedStudent.objects\
            .using(self.from_db_alias)\
            .select_related('user', 'period', 'period__parentnode')
        self.assertEqual(
            related_examiner_migratedb_queryset.get().user.shortname,
            'migrate_user')
        self.assertEqual(
            related_examiner_migratedb_queryset.get().period.parentnode.short_name,
            'migrate_subject')
        self.assertEqual(
            related_examiner_migratedb_queryset.get().period.short_name,
            'migrate_period')

    def test_user_period_subject_not_imported(self):
        self.__create_for_migrate_db(user_shortname='migrate_user', subject_short_name='migrate_subject',
                                     period_short_name='migrate_period')
        with self.assertRaisesMessage(ValueError,
                                      'Users, Subjects and Periods must be imported before RelatedStudents.'):
            relateduser_merger.RelatedStudentMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_user_period_not_imported(self):
        # Default database data
        mommy.make('core.Subject', short_name='migrate_subject')

        # Migrate database data
        self.__create_for_migrate_db(user_shortname='migrate_user', subject_short_name='migrate_subject',
                                     period_short_name='migrate_period')
        with self.assertRaisesMessage(ValueError,
                                      'Users, Subjects and Periods must be imported before RelatedStudents.'):
            relateduser_merger.RelatedStudentMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_user_not_imported(self):
        # Default database data
        subject = mommy.make('core.Subject', short_name='migrate_subject')
        mommy.make('core.Period', short_name='migrate_period', parentnode=subject)

        # Migrate database data
        self.__create_for_migrate_db(user_shortname='migrate_user', subject_short_name='migrate_subject',
                                     period_short_name='migrate_period')
        with self.assertRaisesMessage(ValueError,
                                      'Users, Subjects and Periods must be imported before RelatedStudents.'):
            relateduser_merger.RelatedStudentMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_related_student_imported_sanity(self):
        # Default database data
        default_db_subject = mommy.make('core.Subject', id=105, short_name='migrate_subject')
        default_db_period = mommy.make('core.Period', id=105, short_name='migrate_period',
                                       parentnode=default_db_subject)
        default_db_user = mommy.make(settings.AUTH_USER_MODEL, id=105, shortname='migrate_user')

        # Migrate database data
        self.__create_for_migrate_db(user_shortname='migrate_user', subject_short_name='migrate_subject',
                                     period_short_name='migrate_period')
        self.assertEqual(core_models.RelatedStudent.objects.count(), 0)
        relateduser_merger.RelatedStudentMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.RelatedStudent.objects.count(), 1)
        self.assertEqual(core_models.RelatedStudent.objects.get().user, default_db_user)
        self.assertEqual(core_models.RelatedStudent.objects.get().user.shortname, 'migrate_user')
        self.assertEqual(core_models.RelatedStudent.objects.get().period, default_db_period)
        self.assertEqual(core_models.RelatedStudent.objects.get().period.short_name, 'migrate_period')
        self.assertEqual(core_models.RelatedStudent.objects.get().period.parentnode, default_db_subject)
        self.assertEqual(core_models.RelatedStudent.objects.get().period.parentnode.short_name, 'migrate_subject')

    def test_import_does_not_affect_existing_related_student(self):
        # Default database data
        default_relatedstudent_kwargs = {
            'candidate_id': 'd_candID',
            'automatic_anonymous_id': 'd_aaID',
            'tags': 'd_tag1,d_tag2,d_tag3'
        }
        self.__create_for_default_db(user_shortname='default_user', subject_short_name='default_subject',
                                     period_short_name='default_period', with_related_student=True,
                                     related_student_kwargs=default_relatedstudent_kwargs)
        self.__create_for_default_db(user_shortname='migrate_user', subject_short_name='migrate_subject',
                                     period_short_name='migrate_period')

        # Migrate database data
        migrate_relatedstudent_kwargs = {
            'candidate_id': 'm_candID',
            'automatic_anonymous_id': 'm_aaID',
            'tags': 'm_tag1,m_tag2,m_tag3'
        }
        self.__create_for_migrate_db(user_shortname='migrate_user', subject_short_name='migrate_subject',
                                     period_short_name='migrate_period',
                                     related_student_kwargs=migrate_relatedstudent_kwargs)

        relateduser_merger.RelatedStudentMerger(from_db_alias=self.from_db_alias, transaction=True).run()

        # Test existing RelatedStudent
        default_related_student = core_models.RelatedStudent.objects.get(user__shortname='default_user')
        self.assertEqual(default_related_student.candidate_id, 'd_candID')
        self.assertEqual(default_related_student.automatic_anonymous_id, 'd_aaID')
        self.assertEqual(default_related_student.tags, 'd_tag1,d_tag2,d_tag3')

        # Test migrated RelatedStudent
        migrated_related_student = core_models.RelatedStudent.objects.get(user__shortname='migrate_user')
        self.assertEqual(migrated_related_student.candidate_id, 'm_candID')
        self.assertEqual(migrated_related_student.automatic_anonymous_id, 'm_aaID')
        self.assertEqual(migrated_related_student.tags, 'm_tag1,m_tag2,m_tag3')
