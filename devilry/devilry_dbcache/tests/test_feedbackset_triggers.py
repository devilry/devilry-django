import unittest

from django import test
from django.db import IntegrityError
from django.utils import timezone
from model_mommy import mommy

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_group.models import FeedbackSetDeadlineHistory
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy


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

    def test_group_delete_deletes_feedbackset_history(self):
        assignment = mommy.make('core.Assignment')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedback_set = group.feedbackset_set.first()
        feedback_set.deadline_datetime = timezone.now() + timezone.timedelta(days=1)
        feedback_set.save()
        self.assertEquals(1, AssignmentGroup.objects.count())
        self.assertEquals(1, FeedbackSet.objects.count())
        self.assertEquals(1, FeedbackSetDeadlineHistory.objects.count())
        group.delete()
        self.assertEquals(0, AssignmentGroup.objects.count())
        self.assertEquals(0, FeedbackSet.objects.count())
        self.assertEquals(0, FeedbackSetDeadlineHistory.objects.count())

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

    def test_on_create_feedbackset_no_deadline_history_created(self):
        assignment = mommy.make('core.Assignment')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        self.assertEquals(0, FeedbackSetDeadlineHistory.objects.filter(feedback_set__group_id=group.id).count())

    def test_on_feedbackset_new_attempt_no_deadline_history_created(self):
        assignment = mommy.make('core.Assignment')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_first_attempt_published(group=group)
        group_mommy.feedbackset_new_attempt_unpublished(
            group=group,
            deadline_datetime=timezone.now() + timezone.timedelta(days=1))
        self.assertEquals(0, FeedbackSetDeadlineHistory.objects.count())

    def test_history_assignment_first_deadline_update(self):
        old_first_deadline = timezone.now()
        assignment = mommy.make('core.Assignment', first_deadline=old_first_deadline)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)

        new_first_deadline = timezone.now() + timezone.timedelta(days=1)
        assignment.first_deadline = new_first_deadline
        assignment.save()
        feedback_set = group.feedbackset_set.first()
        self.assertEquals(feedback_set.deadline_datetime, new_first_deadline)
        deadline_history = FeedbackSetDeadlineHistory.objects.get(feedback_set_id=feedback_set.id)
        self.assertIsNotNone(deadline_history.changed_datetime)
        self.assertEquals(deadline_history.deadline_old, old_first_deadline)
        self.assertEquals(deadline_history.deadline_new, new_first_deadline)

    def test_history_feedbackset_first_attempt_deadline_change(self):
        assignment = mommy.make('core.Assignment')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedback_set = group.feedbackset_set.first()
        new_feedbackset_deadline = timezone.now() + timezone.timedelta(days=1)
        feedback_set.deadline_datetime = new_feedbackset_deadline
        feedback_set.save()

        updated_feedback_set = FeedbackSet.objects.get(id=feedback_set.id)
        deadline_history = FeedbackSetDeadlineHistory.objects.get(feedback_set_id=updated_feedback_set.id)
        self.assertEquals(updated_feedback_set.feedbackset_type, FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT)
        self.assertIsNotNone(deadline_history.changed_datetime)
        self.assertEquals(deadline_history.deadline_old, assignment.first_deadline)
        self.assertEquals(deadline_history.deadline_new, updated_feedback_set.deadline_datetime)

    def test_history_feedbackset_new_attempt_deadline_change(self):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_first_attempt_published(group=group)
        new_attempt_deadline = timezone.now() + timezone.timedelta(days=1)
        new_attempt_deadline = new_attempt_deadline.replace(microsecond=0)
        feedback_set_new_attempt = group_mommy.feedbackset_new_attempt_unpublished(
            group=group,
            deadline_datetime=new_attempt_deadline)
        self.assertEquals(0, FeedbackSetDeadlineHistory.objects.filter(feedback_set__group_id=group.id).count())

        new_attempt_updated_deadline = new_attempt_deadline + timezone.timedelta(days=1)
        feedback_set_new_attempt.deadline_datetime = new_attempt_updated_deadline
        feedback_set_new_attempt.save()

        updated_feedback_set = FeedbackSet.objects.get(id=feedback_set_new_attempt.id)
        deadline_history = FeedbackSetDeadlineHistory.objects.get(feedback_set_id=updated_feedback_set.id)
        self.assertIsNotNone(deadline_history.changed_datetime)
        self.assertEquals(new_attempt_deadline, deadline_history.deadline_old)
        self.assertEquals(new_attempt_updated_deadline, deadline_history.deadline_new)

    def test_history_feedbackset_deadline_datetime_multiple_changes(self):
        assignment = mommy.make('core.Assignment')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedback_set = group.feedbackset_set.first()

        deadline_first_change = timezone.now()
        feedback_set.deadline_datetime = deadline_first_change
        feedback_set.save()

        deadline_second_change = timezone.now()
        feedback_set.deadline_datetime = deadline_second_change
        feedback_set.save()

        deadline_third_change = timezone.now()
        feedback_set.deadline_datetime = deadline_third_change
        feedback_set.save()

        deadline_history = FeedbackSetDeadlineHistory.objects\
            .filter(feedback_set_id=feedback_set.id)\
            .order_by('-changed_datetime')
        self.assertEquals(3, deadline_history.count())

        self.assertIsNotNone(deadline_history[0].changed_datetime)
        self.assertEquals(deadline_history[0].deadline_old, assignment.first_deadline)
        self.assertEquals(deadline_history[0].deadline_new, deadline_first_change)

        self.assertIsNotNone(deadline_history[1].changed_datetime)
        self.assertEquals(deadline_history[1].deadline_old, deadline_first_change)
        self.assertEquals(deadline_history[1].deadline_new, deadline_second_change)

        self.assertIsNotNone(deadline_history[2].changed_datetime)
        self.assertEquals(deadline_history[2].deadline_old, deadline_second_change)
        self.assertEquals(deadline_history[2].deadline_new, deadline_third_change)
