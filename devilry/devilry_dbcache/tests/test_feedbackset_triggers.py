from django import test
from django.db import IntegrityError
from django.utils import timezone
from model_mommy import mommy

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group.models import FeedbackSet


class TestFeedbackSetTriggers(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_autocreated_feedbackset_passes_validation(self):
        # Should do nothing because validation is not called
        # when the FeedbackSet is created via a trigger
        mommy.make('core.AssignmentGroup')  # No IntegrityError

    def test_can_delete_group(self):
        group = mommy.make('core.AssignmentGroup')
        self.assertEqual(AssignmentGroup.objects.count(), 1)
        self.assertEqual(FeedbackSet.objects.count(), 1)
        group.delete()
        self.assertEqual(AssignmentGroup.objects.count(), 0)
        self.assertEqual(FeedbackSet.objects.count(), 0)

    def test_first_feedbackset_must_have_deadline_datetime_none(self):
        group = mommy.make('core.AssignmentGroup')
        first_feedbackset = group.feedbackset_set.first()
        first_feedbackset.deadline_datetime = timezone.now()
        with self.assertRaisesMessage(
                IntegrityError,
                'The first FeedbackSet in an AssignmentGroup must have deadline_datetime=NULL'):
            first_feedbackset.save()

    def test_only_first_feedbackset_can_have_deadline_datetime_none(self):
        group = mommy.make('core.AssignmentGroup')
        with self.assertRaisesMessage(
                IntegrityError,
                'Only the first FeedbackSet in an AssignmentGroup can have deadline_datetime=NULL'):
            mommy.make('devilry_group.FeedbackSet',
                       group=group,
                       deadline_datetime=None)
