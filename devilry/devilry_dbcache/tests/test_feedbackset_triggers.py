import unittest

from django import test
from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone
from model_bakery import baker

from devilry.apps.core.models import AssignmentGroup, Assignment
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_group.models import FeedbackSetDeadlineHistory
from devilry.devilry_group.models import FeedbackSetGradingUpdateHistory
from devilry.devilry_group import devilry_group_baker_factories as group_baker


class TestFeedbackSetTriggers(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_autocreated_feedbackset_passes_validation(self):
        # Should do nothing because validation is not called
        # when the FeedbackSet is created via a trigger
        baker.make('core.AssignmentGroup')  # No IntegrityError

    def test_can_delete_group(self):
        group = baker.make('core.AssignmentGroup')
        self.assertEqual(AssignmentGroup.objects.count(), 1)
        self.assertEqual(FeedbackSet.objects.count(), 1)
        group.delete()
        self.assertEqual(AssignmentGroup.objects.count(), 0)
        self.assertEqual(FeedbackSet.objects.count(), 0)

    def test_group_delete_deletes_feedbackset_history(self):
        assignment = baker.make('core.Assignment')
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        feedback_set = group.feedbackset_set.first()
        feedback_set.deadline_datetime = timezone.now() + timezone.timedelta(days=1)
        feedback_set.save()
        self.assertEqual(1, AssignmentGroup.objects.count())
        self.assertEqual(1, FeedbackSet.objects.count())
        self.assertEqual(1, FeedbackSetDeadlineHistory.objects.count())
        group.delete()
        self.assertEqual(0, AssignmentGroup.objects.count())
        self.assertEqual(0, FeedbackSet.objects.count())
        self.assertEqual(0, FeedbackSetDeadlineHistory.objects.count())

    def test_first_feedbackset_deadline_datetime_is_assignment_first_deadline(self):
        assignment = baker.make('core.Assignment')
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        first_feedbackset = group.feedbackset_set.first()
        self.assertEqual(first_feedbackset.deadline_datetime,
                          assignment.first_deadline)

    def test_first_feedbackset_is_updated_on_assignment_first_deadline_change(self):
        old_first_deadline = timezone.now()
        assignment = baker.make('core.Assignment', first_deadline=old_first_deadline)
        group = baker.make('core.AssignmentGroup', parentnode=assignment)

        # Change assignment first_deadline
        new_first_deadline = timezone.now() + timezone.timedelta(days=10)
        assignment.first_deadline = new_first_deadline
        assignment.save()
        first_feedbackset = group.feedbackset_set.first()
        self.assertEqual(first_feedbackset.deadline_datetime, new_first_deadline)

    def test_all_first_feedbacksets_updated_on_assignment_first_deadline_change(self):
        old_first_deadline = timezone.now()
        assignment = baker.make('core.Assignment', first_deadline=old_first_deadline)
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment)
        group2 = baker.make('core.AssignmentGroup', parentnode=assignment)
        group3 = baker.make('core.AssignmentGroup', parentnode=assignment)
        group4 = baker.make('core.AssignmentGroup', parentnode=assignment)
        group5 = baker.make('core.AssignmentGroup', parentnode=assignment)

        # Change assignment first_deadline
        new_first_deadline = timezone.now() + timezone.timedelta(days=10)
        assignment.first_deadline = new_first_deadline
        assignment.save()

        self.assertEqual(group1.feedbackset_set.first().deadline_datetime, new_first_deadline)
        self.assertEqual(group2.feedbackset_set.first().deadline_datetime, new_first_deadline)
        self.assertEqual(group3.feedbackset_set.first().deadline_datetime, new_first_deadline)
        self.assertEqual(group4.feedbackset_set.first().deadline_datetime, new_first_deadline)
        self.assertEqual(group5.feedbackset_set.first().deadline_datetime, new_first_deadline)

    def test_first_feedbackset_deadline_datetime_not_same_as_assignment_first_deadline_is_not_updated(self):
        # The usecase where the deadline_datetime of a FeedbackSet is changed individually.
        assignment = baker.make('core.Assignment')
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment)
        group2 = baker.make('core.AssignmentGroup', parentnode=assignment)

        # Individual deadline change on FeedbackSet for group2
        feedbackset2 = group2.feedbackset_set.first()
        feedbackset2.deadline_datetime = timezone.now() + timezone.timedelta(days=10)
        feedbackset2.save()

        # Change assignment first_deadline
        new_assignment_first_deadline = timezone.now() + timezone.timedelta(days=1)
        assignment.first_deadline = new_assignment_first_deadline
        assignment.save()
        self.assertEqual(group1.feedbackset_set.first().deadline_datetime, new_assignment_first_deadline)
        self.assertNotEqual(feedbackset2.deadline_datetime, assignment.first_deadline)

    def test_on_create_feedbackset_no_deadline_history_created(self):
        assignment = baker.make('core.Assignment')
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        self.assertEqual(0, FeedbackSetDeadlineHistory.objects.filter(feedback_set__group_id=group.id).count())

    def test_on_feedbackset_new_attempt_no_deadline_history_created(self):
        assignment = baker.make('core.Assignment')
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        group_baker.feedbackset_first_attempt_published(group=group)
        group_baker.feedbackset_new_attempt_unpublished(
            group=group,
            deadline_datetime=timezone.now() + timezone.timedelta(days=1))
        self.assertEqual(0, FeedbackSetDeadlineHistory.objects.count())

    def test_history_assignment_first_deadline_update(self):
        old_first_deadline = timezone.now()
        assignment = baker.make('core.Assignment', first_deadline=old_first_deadline)
        group = baker.make('core.AssignmentGroup', parentnode=assignment)

        new_first_deadline = timezone.now() + timezone.timedelta(days=1)
        assignment.first_deadline = new_first_deadline
        assignment.save()
        feedback_set = group.feedbackset_set.first()
        self.assertEqual(feedback_set.deadline_datetime, new_first_deadline)
        deadline_history = FeedbackSetDeadlineHistory.objects.get(feedback_set_id=feedback_set.id)
        self.assertIsNotNone(deadline_history.changed_datetime)
        self.assertEqual(deadline_history.deadline_old, old_first_deadline)
        self.assertEqual(deadline_history.deadline_new, new_first_deadline)

    def test_history_feedbackset_first_attempt_deadline_change_changed_by_user_is_set(self):
        assignment = baker.make('core.Assignment')
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        user = baker.make(settings.AUTH_USER_MODEL)
        feedback_set = group.feedbackset_set.first()
        new_feedbackset_deadline = timezone.now() + timezone.timedelta(days=1)
        feedback_set.deadline_datetime = new_feedbackset_deadline
        feedback_set.last_updated_by = user
        feedback_set.save()

        updated_feedback_set = FeedbackSet.objects.get(id=feedback_set.id)
        deadline_history = FeedbackSetDeadlineHistory.objects.get(feedback_set_id=updated_feedback_set.id)
        self.assertEqual(deadline_history.changed_by, user)

    def test_history_feedbackset_first_attempt_deadline_change(self):
        assignment = baker.make('core.Assignment')
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        feedback_set = group.feedbackset_set.first()
        new_feedbackset_deadline = timezone.now() + timezone.timedelta(days=1)
        feedback_set.deadline_datetime = new_feedbackset_deadline
        feedback_set.save()

        updated_feedback_set = FeedbackSet.objects.get(id=feedback_set.id)
        deadline_history = FeedbackSetDeadlineHistory.objects.get(feedback_set_id=updated_feedback_set.id)
        self.assertEqual(updated_feedback_set.feedbackset_type, FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT)
        self.assertIsNotNone(deadline_history.changed_datetime)
        self.assertEqual(deadline_history.deadline_old, assignment.first_deadline)
        self.assertEqual(deadline_history.deadline_new, updated_feedback_set.deadline_datetime)

    def test_history_feedbackset_new_attempt_deadline_change_changed_by_user_is_set(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        group_baker.feedbackset_first_attempt_published(group=group)
        new_attempt_deadline = timezone.localtime(timezone.now() + timezone.timedelta(days=1))
        new_attempt_deadline = new_attempt_deadline.replace(microsecond=0)
        user = baker.make(settings.AUTH_USER_MODEL)
        feedback_set_new_attempt = group_baker.feedbackset_new_attempt_unpublished(
            group=group,
            deadline_datetime=new_attempt_deadline,
            last_updated_by=user)
        self.assertEqual(0, FeedbackSetDeadlineHistory.objects.filter(feedback_set__group_id=group.id).count())

        new_attempt_updated_deadline = new_attempt_deadline + timezone.timedelta(days=1)
        feedback_set_new_attempt.deadline_datetime = new_attempt_updated_deadline
        feedback_set_new_attempt.save()

        updated_feedback_set = FeedbackSet.objects.get(id=feedback_set_new_attempt.id)
        deadline_history = FeedbackSetDeadlineHistory.objects.get(feedback_set_id=updated_feedback_set.id)
        self.assertEqual(deadline_history.changed_by, user)

    def test_history_feedbackset_new_attempt_deadline_change(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        group_baker.feedbackset_first_attempt_published(group=group)
        new_attempt_deadline = timezone.localtime(timezone.now() + timezone.timedelta(days=1))
        new_attempt_deadline = new_attempt_deadline.replace(microsecond=0)
        feedback_set_new_attempt = group_baker.feedbackset_new_attempt_unpublished(
            group=group,
            deadline_datetime=new_attempt_deadline)
        self.assertEqual(0, FeedbackSetDeadlineHistory.objects.filter(feedback_set__group_id=group.id).count())

        new_attempt_updated_deadline = new_attempt_deadline + timezone.timedelta(days=1)
        feedback_set_new_attempt.deadline_datetime = new_attempt_updated_deadline
        feedback_set_new_attempt.save()

        updated_feedback_set = FeedbackSet.objects.get(id=feedback_set_new_attempt.id)
        deadline_history = FeedbackSetDeadlineHistory.objects.get(feedback_set_id=updated_feedback_set.id)
        self.assertIsNotNone(deadline_history.changed_datetime)
        self.assertEqual(new_attempt_deadline, deadline_history.deadline_old)
        self.assertEqual(new_attempt_updated_deadline, deadline_history.deadline_new)

    def test_history_feedbackset_deadline_datetime_multiple_changes(self):
        assignment = baker.make('core.Assignment')
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
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
        self.assertEqual(3, deadline_history.count())

        self.assertIsNotNone(deadline_history[0].changed_datetime)
        self.assertEqual(deadline_history[0].deadline_old, assignment.first_deadline)
        self.assertEqual(deadline_history[0].deadline_new, deadline_first_change)

        self.assertIsNotNone(deadline_history[1].changed_datetime)
        self.assertEqual(deadline_history[1].deadline_old, deadline_first_change)
        self.assertEqual(deadline_history[1].deadline_new, deadline_second_change)

        self.assertIsNotNone(deadline_history[2].changed_datetime)
        self.assertEqual(deadline_history[2].deadline_old, deadline_second_change)
        self.assertEqual(deadline_history[2].deadline_new, deadline_third_change)


class TestFeedbackSetGradingUpdateTrigger(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_feedbackset_grading_points_updated_sanity(self):
        testgroup = baker.make('core.AssignmentGroup')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        test_feedbackset = group_baker.feedbackset_first_attempt_published(group=testgroup, grading_points=0)
        self.assertEqual(FeedbackSetGradingUpdateHistory.objects.count(), 0)
        test_feedbackset.publish(published_by=testuser, grading_points=1)
        self.assertEqual(FeedbackSetGradingUpdateHistory.objects.count(), 1)

    def test_feedbackset_grading_points_results_simple(self):
        testgroup = baker.make('core.AssignmentGroup')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        first_publish_datetime = timezone.now() - timezone.timedelta(days=10)
        test_feedbackset = group_baker.feedbackset_first_attempt_published(
            group=testgroup, grading_points=0, grading_published_datetime=first_publish_datetime)
        old_published_by = test_feedbackset.grading_published_by

        self.assertEqual(FeedbackSetGradingUpdateHistory.objects.count(), 0)
        test_feedbackset.last_updated_by = testuser
        test_feedbackset.publish(published_by=testuser, grading_points=1)

        update_history = FeedbackSetGradingUpdateHistory.objects.get()
        self.assertEqual(update_history.feedback_set, test_feedbackset)
        self.assertEqual(update_history.updated_by, testuser)
        self.assertTrue(update_history.updated_datetime > first_publish_datetime)
        self.assertEqual(update_history.old_grading_points, 0)
        self.assertEqual(update_history.old_grading_published_by, old_published_by)
        self.assertEqual(update_history.old_grading_published_datetime, first_publish_datetime)

    def test_feedbackset_grading_points_results_multiple(self):
        testassignment = baker.make('core.Assignment', max_points=10,
                                    grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        first_publish_datetime = timezone.now() - timezone.timedelta(days=10)
        test_feedbackset = group_baker.feedbackset_first_attempt_published(
            group=testgroup, grading_points=0, grading_published_datetime=first_publish_datetime)
        first_update_published_by = test_feedbackset.grading_published_by
        self.assertEqual(FeedbackSetGradingUpdateHistory.objects.count(), 0)

        testuser1 = baker.make(settings.AUTH_USER_MODEL)
        testuser2 = baker.make(settings.AUTH_USER_MODEL)
        testuser3 = baker.make(settings.AUTH_USER_MODEL)

        test_feedbackset.publish(published_by=testuser1, grading_points=3)
        test_feedbackset.publish(published_by=testuser2, grading_points=6)
        test_feedbackset.publish(published_by=testuser3, grading_points=10)

        self.assertEqual(FeedbackSetGradingUpdateHistory.objects.count(), 3)

        grading_history_queryset = FeedbackSetGradingUpdateHistory.objects.order_by('updated_datetime')
        grading_history1 = grading_history_queryset[0]
        grading_history2 = grading_history_queryset[1]
        grading_history3 = grading_history_queryset[2]

        # Test history entry for the first update
        self.assertEqual(grading_history1.feedback_set, test_feedbackset)
        self.assertEqual(grading_history1.old_grading_points, 0)
        self.assertEqual(grading_history1.old_grading_published_by, first_update_published_by)

        # Test history entry for the second update
        self.assertEqual(grading_history2.feedback_set, test_feedbackset)
        self.assertEqual(grading_history2.old_grading_points, 3)
        self.assertEqual(grading_history2.old_grading_published_by, testuser1)

        # Test history entry for the third update
        self.assertEqual(grading_history3.feedback_set, test_feedbackset)
        self.assertEqual(grading_history3.old_grading_points, 6)
        self.assertEqual(grading_history3.old_grading_published_by, testuser2)

        # Test final result on the feedbackset
        test_feedbackset = FeedbackSet.objects.get(id=test_feedbackset.id)
        self.assertEqual(test_feedbackset.grading_points, 10)
        self.assertEqual(test_feedbackset.grading_published_by, testuser3)
