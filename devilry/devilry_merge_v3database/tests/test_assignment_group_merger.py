import datetime

import pytz
from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import override_settings
from django.utils import timezone

from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_account import models as account_models
from devilry.devilry_merge_v3database.utils import assignment_merger


class TestAssignmentMerger(test.TestCase):
    from_db_alias = 'migrate_from'
    multi_db = True

    def __create_subject(self, subject_kwargs=None):
        if not subject_kwargs:
            subject_kwargs = {'short_name': 'default_subject'}
        subject = mommy.prepare('core.Subject', **subject_kwargs)
        return subject

    def __create_period(self, subject, period_kwargs=None):
        if not period_kwargs:
            period_kwargs = {'short_name': 'default_period'}
        period = mommy.prepare('core.Period', parentnode=subject, **period_kwargs)
        return period

    def __create_assignment(self, period, assignment_kwargs):
        if not assignment_kwargs:
            assignment_kwargs = {'short_name': 'default_assignment'}
        assignment = mommy.prepare('core.Assignment', parentnode=period, **assignment_kwargs)
        return assignment

    def __create_for_default_db(self, subject_kwargs=None, period_kwargs=None,
                                with_assignment=False, assignment_kwargs=None):
        subject = self.__create_subject(subject_kwargs=subject_kwargs)
        subject.save()
        period = self.__create_period(subject=subject, period_kwargs=period_kwargs)
        period.save()
        if with_assignment:
            assignment = self.__create_assignment(period=period, assignment_kwargs=assignment_kwargs)
            assignment.save()

    def __create_for_migrate_db(self, subject_kwargs=None, period_kwargs=None, assignment_kwargs=None):
        if not subject_kwargs:
            subject_kwargs = {'short_name': 'migrate_subject'}
        if not period_kwargs:
            period_kwargs = {'short_name': 'migrate_period'}
        if not assignment_kwargs:
            assignment_kwargs = {'short_name': 'migrate_assignment'}
        subject = self.__create_subject(subject_kwargs=subject_kwargs)
        subject.save(using=self.from_db_alias)
        period = self.__create_period(subject=subject, period_kwargs=period_kwargs)
        period.save(using=self.from_db_alias)
        assignment = self.__create_assignment(period=period, assignment_kwargs=assignment_kwargs)
        assignment.save(using=self.from_db_alias)

    def test_database_sanity(self):
        # Default database sanity
        self.__create_for_default_db(with_assignment=True)

        # Migrate database data
        self.__create_for_migrate_db()

        # Test default database
        self.assertEqual(core_models.Assignment.objects.count(), 1)
        self.assertEqual(core_models.Assignment.objects.get().short_name, 'default_assignment')
        self.assertEqual(core_models.Assignment.objects.get().parentnode.short_name, 'default_period')
        self.assertEqual(core_models.Assignment.objects.get().parentnode.parentnode.short_name, 'default_subject')

        # Test migrate database
        migrate_db_queryset = core_models.Assignment.objects.using(self.from_db_alias)
        self.assertEqual(migrate_db_queryset.count(), 1)
        self.assertEqual(migrate_db_queryset.get().short_name, 'migrate_assignment')
        self.assertEqual(migrate_db_queryset.get().parentnode.short_name, 'migrate_period')
        self.assertEqual(migrate_db_queryset.get().parentnode.parentnode.short_name, 'migrate_subject')

    def test_period_not_imported(self):
        # Default database
        self.__create_for_default_db(
            subject_kwargs={'short_name': 'migrate_subject'},
            period_kwargs={'short_name': 'default_period'},
            with_assignment=True, assignment_kwargs={'short_name': 'migrate_assignment'})

        # Migrate database
        self.__create_for_migrate_db(
            subject_kwargs={'short_name': 'migrate_subject'},
            period_kwargs={'short_name': 'migrate_period'},
            assignment_kwargs={'short_name': 'migrate_assignment'})

        with self.assertRaisesMessage(ValueError, 'Periods must be imported before Assignments.'):
            assignment_merger.AssignmentMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_check_existing_assignments_not_affected(self):
        # Default database
        default_first_deadline = datetime.datetime(year=2018, month=1, day=10, tzinfo=pytz.utc)
        default_publishing_time = datetime.datetime(year=2018, month=1, day=2, tzinfo=pytz.utc)
        default_period_start_time = datetime.datetime(year=2018, month=1, day=1, tzinfo=pytz.utc)
        default_period_end_time = datetime.datetime(year=2018, month=6, day=1, tzinfo=pytz.utc)
        default_assignment_kwargs = {
            'short_name': 'default_assignment',
            'long_name': 'Default Assignment',
            'first_deadline': default_first_deadline,
            'publishing_time': default_publishing_time,
            'deadline_handling': core_models.Assignment.DEADLINEHANDLING_HARD,
            'uses_custom_candidate_ids': True,
            'anonymizationmode': core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS,
            'students_can_see_points': True,
            'scale_points_percent': 50,
            'max_points': 10,
            'passing_grade_min_points': 5,
            'points_to_grade_mapper': core_models.Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS,
            'grading_system_plugin_id': core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS
        }
        default_period_kwargs = {
            'start_time': default_period_start_time,
            'end_time': default_period_end_time
        }
        self.__create_for_default_db(
            with_assignment=True,
            assignment_kwargs=default_assignment_kwargs,
            period_kwargs=default_period_kwargs)

        # Migrate database
        migrate_first_deadline = datetime.datetime(year=2017, month=8, day=10, tzinfo=pytz.utc)
        migrate_publishing_time = datetime.datetime(year=2017, month=8, day=2, tzinfo=pytz.utc)
        migrate_period_start_time = datetime.datetime(year=2017, month=8, day=1, tzinfo=pytz.utc)
        migrate_period_end_time = datetime.datetime(year=2018, month=12, day=24, tzinfo=pytz.utc)
        migrate_assignment_kwargs = {
            'short_name': 'migrate_assignment',
            'long_name': 'Migrate Assignment',
            'first_deadline': migrate_first_deadline,
            'publishing_time': migrate_publishing_time,
            'deadline_handling': core_models.Assignment.DEADLINEHANDLING_SOFT,
            'uses_custom_candidate_ids': False,
            'anonymizationmode': core_models.Assignment.ANONYMIZATIONMODE_OFF,
            'students_can_see_points': False,
            'scale_points_percent': 30,
            'max_points': 5,
            'passing_grade_min_points': 2,
            'points_to_grade_mapper': core_models.Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED,
            'grading_system_plugin_id': core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED
        }
        migrate_period_kwargs = {
            'short_name': 'migrate_period',
            'start_time': migrate_period_start_time,
            'end_time': migrate_period_end_time
        }
        self.__create_for_migrate_db(
            assignment_kwargs=migrate_assignment_kwargs,
            period_kwargs=migrate_period_kwargs)
        self.__create_for_default_db(
            subject_kwargs={'short_name': 'migrate_subject'},
            period_kwargs=migrate_period_kwargs)

        assignment_merger.AssignmentMerger(from_db_alias=self.from_db_alias, transaction=True).run()

        default_assignment = core_models.Assignment.objects.get(short_name='default_assignment')
        migrate_assignment = core_models.Assignment.objects.get(short_name='migrate_assignment')
        self.assertEqual(default_assignment.short_name, 'default_assignment')
        self.assertEqual(migrate_assignment.short_name, 'migrate_assignment')

        self.assertEqual(default_assignment.long_name, 'Default Assignment')
        self.assertEqual(migrate_assignment.long_name, 'Migrate Assignment')

        self.assertEqual(default_assignment.first_deadline, default_first_deadline)
        self.assertEqual(migrate_assignment.first_deadline, migrate_first_deadline)

        self.assertEqual(default_assignment.publishing_time, default_publishing_time)
        self.assertEqual(migrate_assignment.publishing_time, migrate_publishing_time)

        self.assertEqual(default_assignment.deadline_handling, core_models.Assignment.DEADLINEHANDLING_HARD)
        self.assertEqual(migrate_assignment.deadline_handling, core_models.Assignment.DEADLINEHANDLING_SOFT)

        self.assertTrue(default_assignment.uses_custom_candidate_ids)
        self.assertFalse(migrate_assignment.uses_custom_candidate_ids)

        self.assertEqual(default_assignment.anonymizationmode, core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        self.assertEqual(migrate_assignment.anonymizationmode, core_models.Assignment.ANONYMIZATIONMODE_OFF)

        self.assertTrue(default_assignment.students_can_see_points)
        self.assertFalse(migrate_assignment.students_can_see_points)

        self.assertEqual(default_assignment.scale_points_percent, 50)
        self.assertEqual(migrate_assignment.scale_points_percent, 30)

        self.assertEqual(default_assignment.max_points, 10)
        self.assertEqual(migrate_assignment.max_points, 5)

        self.assertEqual(default_assignment.passing_grade_min_points, 5)
        self.assertEqual(migrate_assignment.passing_grade_min_points, 2)

        self.assertEqual(default_assignment.points_to_grade_mapper,
                         core_models.Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS)
        self.assertEqual(migrate_assignment.points_to_grade_mapper,
                         core_models.Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED)

        self.assertEqual(default_assignment.grading_system_plugin_id,
                         core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        self.assertEqual(migrate_assignment.grading_system_plugin_id,
                         core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)

    def test_import_multiple_assignments_on_different_periods_and_subjects(self):
        # Default data
        default_first_deadline = datetime.datetime(year=2018, month=1, day=10, tzinfo=pytz.utc)
        default_publishing_time = datetime.datetime(year=2018, month=1, day=2, tzinfo=pytz.utc)
        default_period_start_time = datetime.datetime(year=2018, month=1, day=1, tzinfo=pytz.utc)
        default_period_end_time = datetime.datetime(year=2018, month=6, day=1, tzinfo=pytz.utc)
        self.__create_for_default_db(with_assignment=True,
                                     period_kwargs={
                                         'short_name': 'default_period',
                                         'start_time': default_period_start_time,
                                         'end_time': default_period_end_time
                                     },
                                     assignment_kwargs={
                                         'short_name': 'default_assignment',
                                         'publishing_time': default_publishing_time,
                                         'first_deadline': default_first_deadline})

        # Migrate data
        self.__create_for_default_db(
            subject_kwargs={
                'short_name': 'migrate_subject_1'},
            period_kwargs={
                'short_name': 'migrate_period_1',
                'start_time': datetime.datetime(year=2017, month=1, day=1, tzinfo=pytz.utc),
                'end_time': datetime.datetime(year=2017, month=12, day=24, tzinfo=pytz.utc)})
        self.__create_for_default_db(
            subject_kwargs={
                'short_name': 'migrate_subject_2'},
            period_kwargs={
                'short_name': 'migrate_period_2',
                'start_time': datetime.datetime(year=2016, month=1, day=1, tzinfo=pytz.utc),
                'end_time': datetime.datetime(year=2016, month=12, day=24, tzinfo=pytz.utc)})
        self.__create_for_migrate_db(
            assignment_kwargs={
                'short_name': 'migrate_assignment_1',
                'first_deadline': datetime.datetime(year=2017, month=8, day=10, tzinfo=pytz.utc),
                'publishing_time': datetime.datetime(year=2017, month=8, day=2, tzinfo=pytz.utc)},
            period_kwargs={'short_name': 'migrate_period_1'},
            subject_kwargs={'short_name': 'migrate_subject_1'})
        self.__create_for_migrate_db(
            assignment_kwargs={
                'short_name': 'migrate_assignment_2',
                'first_deadline': datetime.datetime(year=2016, month=8, day=10, tzinfo=pytz.utc),
                'publishing_time': datetime.datetime(year=2016, month=8, day=2, tzinfo=pytz.utc)},
            period_kwargs={'short_name': 'migrate_period_2'},
            subject_kwargs={'short_name': 'migrate_subject_2'})

        self.assertEqual(core_models.Assignment.objects.count(), 1)
        assignment_merger.AssignmentMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.Assignment.objects.count(), 3)
        self.assertEqual(core_models.Assignment.objects.filter(short_name='default_assignment').count(), 1)
        self.assertEqual(
            core_models.Assignment.objects.filter(short_name='default_assignment').get().parentnode.short_name,
            'default_period')

        self.assertEqual(core_models.Assignment.objects.filter(short_name='migrate_assignment_1').count(), 1)
        self.assertEqual(
            core_models.Assignment.objects.filter(short_name='migrate_assignment_1').get().parentnode.short_name,
            'migrate_period_1')

        self.assertEqual(core_models.Assignment.objects.filter(short_name='migrate_assignment_2').count(), 1)
        self.assertEqual(
            core_models.Assignment.objects.filter(short_name='migrate_assignment_2').get().parentnode.short_name,
            'migrate_period_2')

    def test_import_multiple_assignments_on_same_period(self):
        # Default database data
        default_first_deadline = datetime.datetime(year=2018, month=1, day=10, tzinfo=pytz.utc)
        default_publishing_time = datetime.datetime(year=2018, month=1, day=2, tzinfo=pytz.utc)
        default_period_start_time = datetime.datetime(year=2018, month=1, day=1, tzinfo=pytz.utc)
        default_period_end_time = datetime.datetime(year=2018, month=6, day=1, tzinfo=pytz.utc)
        self.__create_for_default_db(with_assignment=True,
                                     period_kwargs={
                                         'short_name': 'default_period',
                                         'start_time': default_period_start_time,
                                         'end_time': default_period_end_time
                                     },
                                     assignment_kwargs={
                                         'short_name': 'default_assignment',
                                         'publishing_time': default_publishing_time,
                                         'first_deadline': default_first_deadline})

        migrated_subject = self.__create_subject(subject_kwargs={'short_name': 'migrate_subject'})
        migrated_subject.save()
        migrated_period = self.__create_period(
            subject=migrated_subject,
            period_kwargs={
                'short_name': 'migrate_period',
                'start_time': datetime.datetime(year=2018, month=1, day=1, tzinfo=pytz.utc),
                'end_time': datetime.datetime(year=2018, month=7, day=1, tzinfo=pytz.utc)
            })
        migrated_period.save()

        # Migrate database data
        migrate_subject = self.__create_subject(subject_kwargs={'short_name': 'migrate_subject'})
        migrate_subject.save(using=self.from_db_alias)
        migrate_period = self.__create_period(
            subject=migrate_subject,
            period_kwargs={
                'short_name': 'migrate_period',
                'start_time': datetime.datetime(year=2018, month=1, day=1, tzinfo=pytz.utc),
                'end_time': datetime.datetime(year=2018, month=7, day=1, tzinfo=pytz.utc)
            })
        migrate_period.save(using=self.from_db_alias)
        self.__create_assignment(period=migrate_period, assignment_kwargs={
            'short_name': 'migrate_assignment_1',
            'first_deadline': datetime.datetime(year=2018, month=1, day=10, tzinfo=pytz.utc),
            'publishing_time': datetime.datetime(year=2018, month=1, day=2, tzinfo=pytz.utc)
        }).save(using=self.from_db_alias)

        self.__create_assignment(period=migrate_period, assignment_kwargs={
            'short_name': 'migrate_assignment_2',
            'first_deadline': datetime.datetime(year=2018, month=2, day=10, tzinfo=pytz.utc),
            'publishing_time': datetime.datetime(year=2018, month=2, day=2, tzinfo=pytz.utc)
        }).save(using=self.from_db_alias)

        self.__create_assignment(period=migrate_period, assignment_kwargs={
            'short_name': 'migrate_assignment_3',
            'first_deadline': datetime.datetime(year=2018, month=3, day=10, tzinfo=pytz.utc),
            'publishing_time': datetime.datetime(year=2018, month=3, day=2, tzinfo=pytz.utc)
        }).save(using=self.from_db_alias)

        self.__create_assignment(period=migrate_period, assignment_kwargs={
            'short_name': 'migrate_assignment_4',
            'first_deadline': datetime.datetime(year=2018, month=4, day=10, tzinfo=pytz.utc),
            'publishing_time': datetime.datetime(year=2018, month=4, day=2, tzinfo=pytz.utc)
        }).save(using=self.from_db_alias)

        self.__create_assignment(period=migrate_period, assignment_kwargs={
            'short_name': 'migrate_assignment_5',
            'first_deadline': datetime.datetime(year=2018, month=5, day=10, tzinfo=pytz.utc),
            'publishing_time': datetime.datetime(year=2018, month=5, day=2, tzinfo=pytz.utc)
        }).save(using=self.from_db_alias)

        self.__create_assignment(period=migrate_period, assignment_kwargs={
            'short_name': 'migrate_assignment_6',
            'first_deadline': datetime.datetime(year=2018, month=6, day=10, tzinfo=pytz.utc),
            'publishing_time': datetime.datetime(year=2018, month=6, day=2, tzinfo=pytz.utc)
        }).save(using=self.from_db_alias)

        self.assertEqual(core_models.Assignment.objects.count(), 1)
        self.assertEqual(core_models.Assignment.objects.using(self.from_db_alias).count(), 6)
        assignment_merger.AssignmentMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(core_models.Assignment.objects.count(), 7)
        self.assertEqual(
            core_models.Assignment.objects.get(short_name='default_assignment').parentnode.short_name,
            'default_period')
        self.assertEqual(
            core_models.Assignment.objects.get(short_name='migrate_assignment_1').parentnode.short_name,
            'migrate_period')
        self.assertEqual(
            core_models.Assignment.objects.get(short_name='migrate_assignment_2').parentnode.short_name,
            'migrate_period')
        self.assertEqual(
            core_models.Assignment.objects.get(short_name='migrate_assignment_3').parentnode.short_name,
            'migrate_period')
        self.assertEqual(
            core_models.Assignment.objects.get(short_name='migrate_assignment_4').parentnode.short_name,
            'migrate_period')
        self.assertEqual(
            core_models.Assignment.objects.get(short_name='migrate_assignment_5').parentnode.short_name,
            'migrate_period')
        self.assertEqual(
            core_models.Assignment.objects.get(short_name='migrate_assignment_6').parentnode.short_name,
            'migrate_period')
