import unittest

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

    @unittest.skip('Fix feedbackset validation')
    def test_first_feedbackset_must_have_deadline_datetime_none(self):
        group = mommy.make('core.AssignmentGroup')
        first_feedbackset = group.feedbackset_set.first()
        first_feedbackset.deadline_datetime = timezone.now()
        with self.assertRaisesMessage(
                IntegrityError,
                'The first FeedbackSet in an AssignmentGroup must have deadline_datetime=NULL'):
            first_feedbackset.save()

    @unittest.skip('Fix feedbackset validation')
    def test_only_first_feedbackset_can_have_deadline_datetime_none(self):
        group = mommy.make('core.AssignmentGroup')
        with self.assertRaisesMessage(
                IntegrityError,
                'Only the first FeedbackSet in an AssignmentGroup can have deadline_datetime=NULL'):
            mommy.make('devilry_group.FeedbackSet',
                       group=group,
                       deadline_datetime=None)

    def test_first_feedbackset_deadline_datetime_is_assignment_first_deadline(self):
        assignment = mommy.make('core.Assignment')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        first_feedbackset = group.feedbackset_set.first()
        self.assertEquals(first_feedbackset.deadline_datetime,
                          assignment.first_deadline)

    def test_first_feedbackset_is_updated_on_assignment_first_deadline_change(self):
        old_first_deadline = timezone.now()
        assignment = mommy.make('core.Assignment', first_deadline=old_first_deadline)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)

        # Change assignment first_deadline
        new_first_deadline = timezone.now() + timezone.timedelta(days=10)
        assignment.first_deadline = new_first_deadline
        assignment.save()
        first_feedbackset = group.feedbackset_set.first()
        self.assertEquals(first_feedbackset.deadline_datetime, new_first_deadline)

    def test_all_first_feedbacksets_updated_on_assignment_first_deadline_change(self):
        old_first_deadline = timezone.now()
        assignment = mommy.make('core.Assignment', first_deadline=old_first_deadline)
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group3 = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group4 = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group5 = mommy.make('core.AssignmentGroup', parentnode=assignment)

        # Change assignment first_deadline
        new_first_deadline = timezone.now() + timezone.timedelta(days=10)
        assignment.first_deadline = new_first_deadline
        assignment.save()

        self.assertEquals(group1.feedbackset_set.first().deadline_datetime, new_first_deadline)
        self.assertEquals(group2.feedbackset_set.first().deadline_datetime, new_first_deadline)
        self.assertEquals(group3.feedbackset_set.first().deadline_datetime, new_first_deadline)
        self.assertEquals(group4.feedbackset_set.first().deadline_datetime, new_first_deadline)
        self.assertEquals(group5.feedbackset_set.first().deadline_datetime, new_first_deadline)

    def test_first_feedbackset_deadline_datetime_not_same_as_assignment_first_deadline_is_not_updated(self):
        # The usecase where the deadline_datetime of a FeedbackSet is changed individually.
        assignment = mommy.make('core.Assignment')
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment)

        # Individual deadline change on FeedbackSet for group2
        feedbackset2 = group2.feedbackset_set.first()
        feedbackset2.deadline_datetime = timezone.now() + timezone.timedelta(days=10)
        feedbackset2.save()

        # Change assignment first_deadline
        new_assignment_first_deadline = timezone.now() + timezone.timedelta(days=1)
        assignment.first_deadline = new_assignment_first_deadline
        assignment.save()
        self.assertEquals(group1.feedbackset_set.first().deadline_datetime, new_assignment_first_deadline)
        self.assertNotEquals(feedbackset2.deadline_datetime, assignment.first_deadline)
