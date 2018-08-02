from django.conf import settings
from django.utils import timezone

from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_group import models as group_models

from devilry.devilry_merge_v3database.models import TempMergeId
from devilry.devilry_merge_v3database.utils import feedbackset_merger
from devilry.devilry_merge_v3database.tests.utils import MergerTestHelper


class FeedbackSetMergerTestHelper(MergerTestHelper):
    def create_feedback_set(self, assignment_group, feedback_set_kwargs, db_alias='default'):
        if not feedback_set_kwargs:
            feedback_set_kwargs = {}
        feedback_set = mommy.prepare('devilry_group.FeedbackSet', group=assignment_group, **feedback_set_kwargs)
        feedback_set.save(using=db_alias)
        return feedback_set


class TestFeedbackSetMerger(FeedbackSetMergerTestHelper):
    from_db_alias = 'migrate_from'
    multi_db = True

    def __create_for_default_db(self, subject_kwargs=None, period_kwargs=None, assignment_kwargs=None,
                                assignment_group_kwargs=None, with_feedback_set=False, feedback_set_kwargs=None):
        subject = self.get_or_create_subject(subject_kwargs=subject_kwargs)
        period = self.get_or_create_period(subject=subject, period_kwargs=period_kwargs)
        assignment = self.get_or_create_assignment(period=period, assignment_kwargs=assignment_kwargs)
        assignment_group = self.get_or_create_assignment_group(
            assignment=assignment, assignment_group_kwargs=assignment_group_kwargs)
        if with_feedback_set:
            if not feedback_set_kwargs:
                feedback_set_kwargs = {}
            self.create_feedback_set(assignment_group=assignment_group, feedback_set_kwargs=feedback_set_kwargs)

    def __create_for_migrate_db(self, subject_kwargs=None, period_kwargs=None, assignment_kwargs=None,
                                assignment_group_kwargs=None, feedback_set_kwargs=None):
        if not subject_kwargs:
            subject_kwargs = {'short_name': 'migrate_subject'}
        if not period_kwargs:
            period_kwargs = {'short_name': 'migrate_period'}
        if not assignment_kwargs:
            assignment_kwargs = {'short_name': 'migrate_assignment'}
        if not assignment_group_kwargs:
            assignment_group_kwargs = {'name': 'migrate_group'}
        subject = self.get_or_create_subject(subject_kwargs=subject_kwargs, db_alias=self.from_db_alias)
        period = self.get_or_create_period(subject=subject, period_kwargs=period_kwargs, db_alias=self.from_db_alias)
        assignment = self.get_or_create_assignment(period=period, assignment_kwargs=assignment_kwargs,
                                                   db_alias=self.from_db_alias)
        assignment_group = self.get_or_create_assignment_group(
            assignment=assignment, assignment_group_kwargs=assignment_group_kwargs, db_alias=self.from_db_alias)
        if not feedback_set_kwargs:
            feedback_set_kwargs = {}
        self.create_feedback_set(assignment_group=assignment_group,
                                 feedback_set_kwargs=feedback_set_kwargs, db_alias=self.from_db_alias)

    def test_database_sanity(self):
        # Default database data
        self.__create_for_default_db(with_feedback_set=True)

        # Default database data
        self.__create_for_migrate_db()

        # Test default database
        self.assertEqual(group_models.FeedbackSet.objects.count(), 1)
        self.assertEqual(group_models.FeedbackSet.objects.get().group.name, 'default_group')

        # Test migrate database
        self.assertEqual(group_models.FeedbackSet.objects.using(self.from_db_alias).count(), 1)
        self.assertEqual(group_models.FeedbackSet.objects.using(self.from_db_alias).get().group.name, 'migrate_group')

    def test_assignment_group_not_imported_raises_exception(self):
        # Default database data
        self.__create_for_default_db(assignment_group_kwargs={'name': 'default_group'})

        # Migrate database data
        self.__create_for_migrate_db()

        with self.assertRaisesMessage(ValueError, 'AssignmentGroups must be imported before FeedbackSets.'):
            feedbackset_merger.FeedbackSetMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_import_feedbackset_sanity(self):
        # Default database data
        self.__create_for_default_db(
            assignment_group_kwargs={'name': 'migrate_group'}
        )
        created_by_user = mommy.make(settings.AUTH_USER_MODEL, shortname='created_by_user')
        grading_published_by_user = mommy.make(settings.AUTH_USER_MODEL, shortname='graded_by_user')

        # Migrate database data
        migrate_created_by_user = mommy.prepare(settings.AUTH_USER_MODEL, shortname='created_by_user')
        migrate_created_by_user.save(using=self.from_db_alias)
        migrate_published_by_user = mommy.prepare(settings.AUTH_USER_MODEL, shortname='graded_by_user')
        migrate_published_by_user.save(using=self.from_db_alias)
        migrate_feedbackset_data = {
            'feedbackset_type': group_models.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT,
            'deadline_datetime': (timezone.now() - timezone.timedelta(days=2)).replace(microsecond=0),
            'created_by': migrate_created_by_user,
            'grading_published_by': migrate_published_by_user,
            'grading_points': 5,
            'grading_published_datetime': timezone.now() - timezone.timedelta(days=3)
        }
        self.__create_for_migrate_db(
            assignment_group_kwargs={'name': 'migrate_group'},
            feedback_set_kwargs=migrate_feedbackset_data)

        # Create TempMergeId for FeedbackSet
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get().id,
                   to_id=core_models.AssignmentGroup.objects.get().id,
                   model_name='core_assignmentgroup')

        self.assertEqual(group_models.FeedbackSet.objects.count(), 0)
        feedbackset_merger.FeedbackSetMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(group_models.FeedbackSet.objects.count(), 1)
        feedback_set = group_models.FeedbackSet.objects.get()
        self.assertEqual(feedback_set.feedbackset_type, migrate_feedbackset_data['feedbackset_type'])
        self.assertEqual(feedback_set.created_by, created_by_user)
        self.assertEqual(feedback_set.deadline_datetime, migrate_feedbackset_data['deadline_datetime'])
        self.assertEqual(feedback_set.grading_points, migrate_feedbackset_data['grading_points'])
        self.assertEqual(feedback_set.grading_published_by, grading_published_by_user)
        self.assertEqual(feedback_set.grading_published_datetime,
                         migrate_feedbackset_data['grading_published_datetime'])

    def test_existing_feedback_set_in_same_group_not_affected(self):
        # Default database data
        self.__create_for_default_db(
            assignment_group_kwargs={'name': 'migrate_group'},
            with_feedback_set=True,
            feedback_set_kwargs={'feedbackset_type': group_models.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT})

        # Migrate database data
        self.__create_for_migrate_db(
            assignment_group_kwargs={'name': 'migrate_group'},
            feedback_set_kwargs={'feedbackset_type': group_models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT})

        # Create TempMergeId for FeedbackSet
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get().id,
                   to_id=core_models.AssignmentGroup.objects.get().id,
                   model_name='core_assignmentgroup')

        self.assertEqual(group_models.FeedbackSet.objects.count(), 1)
        feedbackset_merger.FeedbackSetMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(group_models.FeedbackSet.objects.count(), 2)
        self.assertTrue(group_models.FeedbackSet.objects.filter(
            feedbackset_type=group_models.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT).exists())
        self.assertTrue(group_models.FeedbackSet.objects.filter(
            feedbackset_type=group_models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT).exists())

    def test_existing_feedback_set_in_different_group_not_affected(self):
        # Default database data
        self.__create_for_default_db(
            assignment_group_kwargs={'name': 'default_group'},
            with_feedback_set=True)
        self.__create_for_default_db(
            assignment_group_kwargs={'name': 'migrate_group'})

        # Migrate database data
        self.__create_for_migrate_db(
            assignment_group_kwargs={'name': 'migrate_group'})

        # Create TempMergeId for FeedbackSet
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get().id,
                   to_id=core_models.AssignmentGroup.objects.get(name='migrate_group').id,
                   model_name='core_assignmentgroup')

        self.assertEqual(group_models.FeedbackSet.objects.count(), 1)
        feedbackset_merger.FeedbackSetMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(group_models.FeedbackSet.objects.filter(group__name='default_group').count(), 1)
        self.assertEqual(group_models.FeedbackSet.objects.filter(group__name='migrate_group').count(), 1)

    def test_import_feedbackset_creates_temp_merge_id(self):
        # Default database data
        self.__create_for_default_db(
            assignment_group_kwargs={'name': 'migrate_group'}
        )

        # Migrate database data
        self.__create_for_migrate_db(
            assignment_group_kwargs={'name': 'migrate_group'},
            feedback_set_kwargs={'id': 512})

        # Create TempMergeId for FeedbackSet
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get().id,
                   to_id=core_models.AssignmentGroup.objects.get(name='migrate_group').id,
                   model_name='core_assignmentgroup')

        self.assertEqual(TempMergeId.objects.filter(model_name='devilry_group_feedbackset').count(), 0)
        feedbackset_merger.FeedbackSetMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(TempMergeId.objects.filter(model_name='devilry_group_feedbackset').count(), 1)
        feedback_set = group_models.FeedbackSet.objects.get()
        temp_merge_id = TempMergeId.objects.get(model_name='devilry_group_feedbackset')
        self.assertEqual(temp_merge_id.to_id, feedback_set.id)
        self.assertEqual(temp_merge_id.from_id, 512)

    def test_import_multiple_feedbacksets_in_same_group(self):
        # Default database data
        self.__create_for_default_db(
            assignment_group_kwargs={'name': 'migrate_group'}
        )

        # Migrate database data
        self.__create_for_migrate_db(
            assignment_group_kwargs={'name': 'migrate_group'},
            feedback_set_kwargs={'id': 500})
        self.__create_for_migrate_db(
            assignment_group_kwargs={'name': 'migrate_group'},
            feedback_set_kwargs={'id': 501})
        self.__create_for_migrate_db(
            assignment_group_kwargs={'name': 'migrate_group'},
            feedback_set_kwargs={'id': 502})

        # Create TempMergeId for FeedbackSet
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get().id,
                   to_id=core_models.AssignmentGroup.objects.get(name='migrate_group').id,
                   model_name='core_assignmentgroup')

        self.assertEqual(TempMergeId.objects.filter(model_name='devilry_group_feedbackset').count(), 0)
        feedbackset_merger.FeedbackSetMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(TempMergeId.objects.filter(model_name='devilry_group_feedbackset').count(), 3)
        self.assertEqual(TempMergeId.objects.filter(model_name='devilry_group_feedbackset', from_id=500).count(), 1)
        self.assertEqual(TempMergeId.objects.filter(model_name='devilry_group_feedbackset', from_id=501).count(), 1)
        self.assertEqual(TempMergeId.objects.filter(model_name='devilry_group_feedbackset', from_id=502).count(), 1)
        self.assertEqual(group_models.FeedbackSet.objects.count(), 3)

    def test_import_multiple_feedbacksets_in_different_groups(self):
        # Default database data
        self.__create_for_default_db(
            assignment_group_kwargs={'name': 'migrate_group_1'}
        )
        self.__create_for_default_db(
            assignment_group_kwargs={'name': 'migrate_group_2'}
        )

        # Migrate database data
        self.__create_for_migrate_db(
            assignment_group_kwargs={'name': 'migrate_group_1'},
            feedback_set_kwargs={'id': 500})
        self.__create_for_migrate_db(
            assignment_group_kwargs={'name': 'migrate_group_1'},
            feedback_set_kwargs={'id': 501})
        self.__create_for_migrate_db(
            assignment_group_kwargs={'name': 'migrate_group_2'},
            feedback_set_kwargs={'id': 502})
        self.__create_for_migrate_db(
            assignment_group_kwargs={'name': 'migrate_group_2'},
            feedback_set_kwargs={'id': 503})

        # Create TempMergeId for FeedbackSet
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get(name='migrate_group_1').id,
                   to_id=core_models.AssignmentGroup.objects.get(name='migrate_group_1').id,
                   model_name='core_assignmentgroup')
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=core_models.AssignmentGroup.objects.using(self.from_db_alias).get(name='migrate_group_2').id,
                   to_id=core_models.AssignmentGroup.objects.get(name='migrate_group_2').id,
                   model_name='core_assignmentgroup')

        self.assertEqual(TempMergeId.objects.filter(model_name='devilry_group_feedbackset').count(), 0)
        feedbackset_merger.FeedbackSetMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(TempMergeId.objects.filter(model_name='devilry_group_feedbackset').count(), 4)
        self.assertEqual(TempMergeId.objects.filter(model_name='devilry_group_feedbackset', from_id=500).count(), 1)
        self.assertEqual(TempMergeId.objects.filter(model_name='devilry_group_feedbackset', from_id=501).count(), 1)
        self.assertEqual(TempMergeId.objects.filter(model_name='devilry_group_feedbackset', from_id=502).count(), 1)
        self.assertEqual(TempMergeId.objects.filter(model_name='devilry_group_feedbackset', from_id=503).count(), 1)
        self.assertEqual(group_models.FeedbackSet.objects.filter(group__name='migrate_group_1').count(), 2)
        self.assertEqual(group_models.FeedbackSet.objects.filter(group__name='migrate_group_2').count(), 2)
