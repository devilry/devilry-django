import unittest

from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group import models as group_models
from devilry.apps.core import models as core_models
from devilry.devilry_comment import models as comment_models


class TestFeedbackSetModel(TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_feedbackset_group(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = group_mommy.make_first_feedbackset_in_group(
            group=testgroup)
        self.assertEquals(feedbackset.group, testgroup)

    def test_feedbackset_feedbackset_type_default_first_try(self):
        feedbackset = group_mommy.make_first_feedbackset_in_group()
        self.assertEquals(feedbackset.feedbackset_type, group_models.FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT)

    def test_feedbackset_created_by(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        feedbackset = group_mommy.make_first_feedbackset_in_group(
            created_by=testuser)
        self.assertEquals(feedbackset.created_by, testuser)

    def test_feedbackset_created_datetime(self):
        feedbackset = group_mommy.make_first_feedbackset_in_group()
        self.assertIsNotNone(feedbackset.created_datetime)

    def test_feedbackset_grading_published_datetime_default_none(self):
        feedbackset = group_mommy.make_first_feedbackset_in_group()
        self.assertIsNone(feedbackset.grading_published_datetime)

    def test_feedbackset_grading_published_datetime(self):
        feedbackset = group_mommy.make_first_feedbackset_in_group(
            grading_published_datetime=timezone.now())
        self.assertIsNotNone(feedbackset.grading_published_datetime)

    def test_feedbackset_grading_published_by_default_none(self):
        feedbackset = group_mommy.make_first_feedbackset_in_group()
        self.assertIsNone(feedbackset.grading_published_by)

    def test_feedbackset_grading_points_default_none(self):
        feedbackset = group_mommy.make_first_feedbackset_in_group()
        self.assertIsNone(feedbackset.grading_points)

    def test_feedbackset_grading_points(self):
        feedbackset = group_mommy.make_first_feedbackset_in_group(grading_points=10)
        self.assertEquals(feedbackset.grading_points, 10)

    def test_feedbackset_current_deadline_first_attempt(self):
        test_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        test_feedbackset = group_mommy.make_first_feedbackset_in_group(
            group__parentnode=test_assignment)
        self.assertEquals(test_feedbackset.current_deadline(), test_assignment.first_deadline)

    def test_feedbackset_current_deadline_not_first_attempt(self):
        test_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        test_feedbackset = mommy.make('devilry_group.FeedbackSet',
                                      group__parentnode=test_assignment,
                                      deadline_datetime=timezone.now(),
                                      feedbackset_type=group_models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT)
        self.assertEquals(test_feedbackset.current_deadline(), test_feedbackset.deadline_datetime)
        self.assertNotEquals(test_feedbackset.current_deadline(), test_assignment.first_deadline)

    def test_feedback_set_publish(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        grading_points = 10
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
                group__parentnode__first_deadline=timezone.now() - timezone.timedelta(days=1))
        result, msg = test_feedbackset.publish(published_by=testuser, grading_points=grading_points)
        self.assertTrue(result)
        self.assertEquals(msg, '')
        self.assertIsNotNone(test_feedbackset.grading_published_datetime)
        self.assertEquals(grading_points, test_feedbackset.grading_points)
        self.assertEquals(testuser, test_feedbackset.grading_published_by)

    def test_feedback_set_publish_multiple_feedbackcomments_order(self):
        examiner = mommy.make('core.Examiner')
        testfeedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group__parentnode__parentnode=mommy.make_recipe('devilry.apps.core.period_active')
        )
        mommy.make('devilry_group.GroupComment',
                   user_role='examiner',
                   user=examiner.relatedexaminer.user,
                   feedback_set=testfeedbackset,
                   part_of_grading=True,
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   text='comment1')
        mommy.make('devilry_group.GroupComment',
                   user_role='examiner',
                   user=examiner.relatedexaminer.user,
                   feedback_set=testfeedbackset,
                   part_of_grading=True,
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   text='comment2')
        mommy.make('devilry_group.GroupComment',
                   user_role='examiner',
                   user=examiner.relatedexaminer.user,
                   feedback_set=testfeedbackset,
                   part_of_grading=True,
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                   text='comment3')
        testfeedbackset.publish(published_by=examiner.relatedexaminer.user, grading_points=1)
        groupcomments = group_models.GroupComment.objects.\
            filter(feedback_set__id=testfeedbackset.id).\
            order_by('published_datetime')
        self.assertEquals(groupcomments[0].text, 'comment1')
        self.assertEquals(groupcomments[1].text, 'comment2')
        self.assertEquals(groupcomments[2].text, 'comment3')

    def test_feedbackset_ignored_without_reason(self):
        test_feedbackset = group_mommy.make_first_feedbackset_in_group(ignored=True)
        with self.assertRaisesMessage(ValidationError, 'FeedbackSet can not be ignored without a reason'):
            test_feedbackset.full_clean()

    def test_feedbackset_not_ignored_with_reason(self):
        test_feedbackset = group_mommy.make_first_feedbackset_in_group(
            ignored_reason='dewey was sick!')
        with self.assertRaisesMessage(ValidationError,
                                      'FeedbackSet can not have a ignored reason without being set to ignored.'):
            test_feedbackset.full_clean()

    def test_feedbackset_ignored_with_grading_published(self):
        test_feedbackset = group_mommy.make_first_feedbackset_in_group(
                                      ignored=True,
                                      ignored_reason='test',
                                      grading_published_datetime=timezone.now())
        with self.assertRaisesMessage(ValidationError,
                                      'Ignored FeedbackSet can not have grading_published_datetime, '
                                      'grading_points or grading_published_by set.'):
            test_feedbackset.full_clean()

    def test_feedbackset_ignored_with_grading_published_by(self):
        test_feedbackset = mommy.prepare(
            'devilry_group.FeedbackSet',
            ignored=True,
            ignored_reason='test',
            grading_published_by=mommy.make(settings.AUTH_USER_MODEL))
        with self.assertRaisesMessage(ValidationError,
                                      'Ignored FeedbackSet can not have grading_published_datetime, '
                                      'grading_points or grading_published_by set.'):
            test_feedbackset.full_clean()

    def test_feedbackset_ignored_with_grading_points(self):
        test_feedbackset = group_mommy.make_first_feedbackset_in_group(
                                      ignored=True,
                                      ignored_reason='test',
                                      grading_points=10)
        with self.assertRaisesMessage(ValidationError,
                                      'Ignored FeedbackSet can not have grading_published_datetime, '
                                      'grading_points or grading_published_by set.'):
            test_feedbackset.full_clean()

    def test_feedbackset_publish_published_by_is_none(self):
        grading_points = 10
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group__parentnode__first_deadline=timezone.now() - timezone.timedelta(days=1))
        with self.assertRaisesMessage(ValidationError,
                                      'A FeedbackSet can not be published without being published by someone.'):
            test_feedbackset.publish(published_by=None, grading_points=grading_points)

    def test_feedbackset_publish_grading_points_is_none(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        test_feedbackset = group_mommy.feedbackset_first_attempt_unpublished(
            group__parentnode__first_deadline=timezone.now() - timezone.timedelta(days=1))
        with self.assertRaisesMessage(ValidationError,
                                      'A FeedbackSet can not be published without providing "points".'):
            test_feedbackset.publish(published_by=testuser, grading_points=None)

    def test_clean_published_by_is_none(self):
        testfeedbackset = mommy.prepare('devilry_group.FeedbackSet',
                                        grading_published_datetime=timezone.now(),
                                        grading_published_by=None,
                                        grading_points=10)
        with self.assertRaisesMessage(ValidationError,
                                      'A FeedbackSet can not be published without being published by someone.'):
            testfeedbackset.clean()

    def test_clean_grading_points_is_none(self):
        testuser = mommy.prepare(settings.AUTH_USER_MODEL)
        testfeedbackset = mommy.prepare('devilry_group.FeedbackSet',
                                        grading_published_datetime=timezone.now(),
                                        grading_published_by=testuser,
                                        grading_points=None)
        with self.assertRaisesMessage(ValidationError,
                                      'A FeedbackSet can not be published without providing "points".'):
            testfeedbackset.clean()

    def __make_assignment(self, first_deadline, deadline_handling=core_models.Assignment.DEADLINEHANDLING_SOFT):
        test_assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        test_assignment.first_deadline = first_deadline
        test_assignment.deadline_handling = deadline_handling
        return test_assignment

    def test_can_add_comment_student_assignment_deadline_hard_expired(self):
        test_assignment = self.__make_assignment(
            first_deadline=timezone.now() - timezone.timedelta(days=1),
            deadline_handling=core_models.Assignment.DEADLINEHANDLING_HARD)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=test_assignment)
        with self.assertRaises(group_models.HardDeadlineExpiredException):
            test_feedbackset.can_add_comment(
                assignment=test_assignment,
                comment_user_role=group_models.GroupComment.USER_ROLE_STUDENT)

    def test_can_add_comment_student_assignment_deadline_soft_expired(self):
        test_assignment = self.__make_assignment(
            first_deadline=timezone.now() - timezone.timedelta(days=1),
            deadline_handling=core_models.Assignment.DEADLINEHANDLING_SOFT)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=test_assignment)
        test_feedbackset.can_add_comment(
            assignment=test_assignment,
            comment_user_role=group_models.GroupComment.USER_ROLE_STUDENT)

    def test_can_add_comment_examiner_assignment_deadline_hard_expired_exception_not_raised(self):
        test_assignment = self.__make_assignment(
            first_deadline=timezone.now() - timezone.timedelta(days=1),
            deadline_handling=core_models.Assignment.DEADLINEHANDLING_HARD)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=test_assignment)
        test_feedbackset.can_add_comment(
            assignment=test_assignment,
            comment_user_role=group_models.GroupComment.USER_ROLE_EXAMINER)

    def test_can_add_comment_admin_assignment_deadline_hard_expired_exception_not_raised(self):
        test_assignment = self.__make_assignment(
            first_deadline=timezone.now() - timezone.timedelta(days=1),
            deadline_handling=core_models.Assignment.DEADLINEHANDLING_HARD)
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=test_assignment)
        test_feedbackset.can_add_comment(
            assignment=test_assignment,
            comment_user_role=group_models.GroupComment.USER_ROLE_ADMIN)

    def test_can_add_comment_student_assignment_period_expired(self):
        test_assignment = mommy.make_recipe('devilry.apps.core.assignment_oldperiod_end')
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=test_assignment)
        with self.assertRaises(group_models.PeriodExpiredException):
            test_feedbackset.can_add_comment(
                assignment=test_assignment,
                comment_user_role=group_models.GroupComment.USER_ROLE_STUDENT)

    def test_can_add_comment_examiner_assignment_period_expired(self):
        test_assignment = mommy.make_recipe('devilry.apps.core.assignment_oldperiod_end')
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=test_assignment)
        with self.assertRaises(group_models.PeriodExpiredException):
            test_feedbackset.can_add_comment(
                assignment=test_assignment,
                comment_user_role=group_models.GroupComment.USER_ROLE_EXAMINER)

    def test_can_add_comment_admin_assignment_period_expired(self):
        test_assignment = mommy.make_recipe('devilry.apps.core.assignment_oldperiod_end')
        test_feedbackset = mommy.make('devilry_group.FeedbackSet', group__parentnode=test_assignment)
        with self.assertRaises(group_models.PeriodExpiredException):
            test_feedbackset.can_add_comment(
                assignment=test_assignment,
                comment_user_role=group_models.GroupComment.USER_ROLE_ADMIN)

    def test_filter_public_comment_files_from_students_sanity(self):
        test_feedbackset = mommy.make('devilry_group.FeedbackSet')
        group_comment = mommy.make('devilry_group.GroupComment', feedback_set=test_feedbackset,
                                   user_role=comment_models.Comment.USER_ROLE_STUDENT)
        mommy.make('devilry_comment.CommentFile', comment=group_comment)
        self.assertIn(test_feedbackset, group_models.FeedbackSet.objects.filter_public_comment_files_from_students())

    def test_filter_public_comment_files_from_students_multiple_feedbacksets_with_and_without_comments(self):
        # Feedbackset 1
        test_feedbackset1 = mommy.make('devilry_group.FeedbackSet')
        group_comment1 = mommy.make('devilry_group.GroupComment', feedback_set=test_feedbackset1,
                                   user_role=comment_models.Comment.USER_ROLE_STUDENT)
        mommy.make('devilry_comment.CommentFile', comment=group_comment1)
        group_comment2 = mommy.make('devilry_group.GroupComment', feedback_set=test_feedbackset1,
                                    user_role=comment_models.Comment.USER_ROLE_STUDENT)
        mommy.make('devilry_comment.CommentFile', comment=group_comment2)

        # Feedbackset 2
        test_feedbackset2 = mommy.make('devilry_group.FeedbackSet')
        group_comment3 = mommy.make('devilry_group.GroupComment', feedback_set=test_feedbackset2,
                                    user_role=comment_models.Comment.USER_ROLE_EXAMINER)
        mommy.make('devilry_comment.CommentFile', comment=group_comment3)
        group_comment4 = mommy.make('devilry_group.GroupComment', feedback_set=test_feedbackset2,
                                    user_role=comment_models.Comment.USER_ROLE_ADMIN)
        mommy.make('devilry_comment.CommentFile', comment=group_comment4)

        # Feedbackset 3
        test_feedbackset3 = mommy.make('devilry_group.FeedbackSet')
        group_comment5 = mommy.make('devilry_group.GroupComment', feedback_set=test_feedbackset3,
                                    user_role=comment_models.Comment.USER_ROLE_STUDENT)
        mommy.make('devilry_comment.CommentFile', comment=group_comment5)

        feedback_set_queryset = group_models.FeedbackSet.objects.filter_public_comment_files_from_students()
        self.assertIn(test_feedbackset1, feedback_set_queryset)
        self.assertNotIn(test_feedbackset2, feedback_set_queryset)
        self.assertIn(test_feedbackset3, feedback_set_queryset)

    def test_filter_public_comment_files_from_students_no_public_student_files(self):
        test_feedbackset = mommy.make('devilry_group.FeedbackSet')
        group_comment_admin = mommy.make('devilry_group.GroupComment', feedback_set=test_feedbackset,
                                         user_role=comment_models.Comment.USER_ROLE_ADMIN)
        group_comment_examiner = mommy.make('devilry_group.GroupComment', feedback_set=test_feedbackset,
                                            user_role=comment_models.Comment.USER_ROLE_EXAMINER)
        mommy.make('devilry_comment.CommentFile', comment=group_comment_admin)
        mommy.make('devilry_comment.CommentFile', comment=group_comment_examiner)
        self.assertNotIn(test_feedbackset, group_models.FeedbackSet.objects.filter_public_comment_files_from_students())

    def test_filter_public_comment_files_from_students_query_count(self):
        test_feedbackset = mommy.make('devilry_group.FeedbackSet')
        group_comment = mommy.make('devilry_group.GroupComment', feedback_set=test_feedbackset,
                                   user_role=comment_models.Comment.USER_ROLE_STUDENT)
        mommy.make('devilry_comment.CommentFile', comment=group_comment)
        with self.assertNumQueries(1):
            self.assertIn(
                test_feedbackset,
                group_models.FeedbackSet.objects.filter_public_comment_files_from_students()
            )
