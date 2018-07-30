from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
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

        # Default database data
        self.__create_for_migrate_db()

        with self.assertRaisesMessage(ValueError, 'AssignmentGroups must be imported before FeedbackSets.'):
            feedbackset_merger.FeedbackSetMerger(from_db_alias=self.from_db_alias, transaction=True).run()

    def test_existing_feedbackset_not_affected(self):
        # Default database data
        default_db_kwarg_data = {
            'subject_kwargs': {'short_name': 'migrate_subject'},
            'period_kwargs': {'short_name': 'migrate_period'},
            'assignment_kwargs': {'short_name': 'migrate_assignment'}
        }
        self.__create_for_default_db(
            assignment_group_kwargs={'name': 'default_group'},
            with_feedbackset=True,
            **default_db_kwarg_data
        )

        # Default database data
        self.__create_for_migrate_db()
