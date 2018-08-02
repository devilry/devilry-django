from devilry.devilry_comment.models import Comment
from django.conf import settings
from django.utils import timezone

from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_group import models as group_models
from devilry.devilry_comment import models as comment_models

from devilry.devilry_merge_v3database.models import TempMergeId
from devilry.devilry_merge_v3database.utils import feedbackset_merger
from devilry.devilry_merge_v3database.utils import comment_merger
from devilry.devilry_merge_v3database.tests.utils import MergerTestHelper


class TestGroupCommentMerger(MergerTestHelper):
    from_db_alias = 'migrate_from'
    multi_db = True

    def create_group_comment(self, feedback_set, group_comment_kwargs, db_alias='default'):
        if not group_comment_kwargs:
            group_comment_kwargs = {}
        group_comment = mommy.prepare('devilry_group.GroupComment', feedback_set=feedback_set, **group_comment_kwargs)
        group_comment.save(using=db_alias)

    def __create_for_default_db(self, subject_kwargs=None, period_kwargs=None, assignment_kwargs=None,
                                assignment_group_kwargs=None, feedback_set_kwargs=None, with_group_comment=False,
                                group_comment_kwargs=None):
        subject = self.get_or_create_subject(subject_kwargs=subject_kwargs)
        period = self.get_or_create_period(subject=subject, period_kwargs=period_kwargs)
        assignment = self.get_or_create_assignment(period=period, assignment_kwargs=assignment_kwargs)
        assignment_group = self.get_or_create_assignment_group(
            assignment=assignment, assignment_group_kwargs=assignment_group_kwargs)
        feedback_set = self.get_or_create_feedback_set(assignment_group=assignment_group,
                                                       feedback_set_kwargs=feedback_set_kwargs)
        if with_group_comment:
            if not group_comment_kwargs:
                group_comment_kwargs = {}
            self.create_group_comment(feedback_set=feedback_set, group_comment_kwargs=group_comment_kwargs)

    def __create_for_migrate_db(self, subject_kwargs=None, period_kwargs=None, assignment_kwargs=None,
                                assignment_group_kwargs=None, feedback_set_kwargs=None, group_comment_kwargs=None):
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
        feedback_set = self.get_or_create_feedback_set(
            assignment_group=assignment_group, feedback_set_kwargs=feedback_set_kwargs, db_alias=self.from_db_alias)
        if not group_comment_kwargs:
            group_comment_kwargs = {}
        self.create_group_comment(
            feedback_set=feedback_set, group_comment_kwargs=group_comment_kwargs, db_alias=self.from_db_alias)

    def test_database_sanity(self):
        # Default database data
        self.__create_for_default_db(with_group_comment=True)

        # Migrate database data
        self.__create_for_migrate_db()

        # Test default database
        self.assertEqual(group_models.GroupComment.objects.count(), 1)
        self.assertEqual(group_models.GroupComment.objects.get().feedback_set.group.name, 'default_group')

        # Test migrate database
        self.assertEqual(group_models.GroupComment.objects.using(self.from_db_alias).count(), 1)
        self.assertEqual(
            group_models.GroupComment.objects.using(self.from_db_alias).get().feedback_set.group.name, 'migrate_group')

    def test_feedback_set_not_imported_raises_exception(self):
        # Default database data
        self.__create_for_default_db(with_group_comment=True)

        # Migrate database data
        self.__create_for_migrate_db()

        # Create TempMergeId for Comment
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=comment_models.Comment.objects.using(self.from_db_alias).get().id,
                   to_id=comment_models.Comment.objects.get().id,
                   model_name='devilry_comment_comment')

        # Create TempMergeId for FeedbackSet
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=group_models.FeedbackSet.objects.using(self.from_db_alias).get().id,
                   to_id=group_models.FeedbackSet.objects.get().id,
                   model_name='devilry_group_feedbackset')

        with self.assertRaisesMessage(ValueError, 'FeedbackSets must be imported before GroupComments'):
            comment_merger.GroupCommentMerger(from_db_alias=self.from_db_alias, transaction=True).run()
