from datetime import timedelta

from django import test
from model_mommy import mommy

from devilry.apps.core.mommy_recipes import ACTIVE_PERIOD_START
from devilry.devilry_comment.models import Comment
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group.models import GroupComment, ImageAnnotationComment


class TestAssignmentGroupCachedDataBasics(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_autocreated_feedbackset_is_correctly_cached(self):
        group = mommy.make('core.AssignmentGroup')
        first_feedbackset = group.feedbackset_set.first()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_feedbackset, first_feedbackset)
        self.assertEqual(group.cached_data.first_feedbackset, first_feedbackset)
        self.assertEqual(group.cached_data.last_published_feedbackset, None)

    def test_first_feedbackset(self):
        group = mommy.make('core.AssignmentGroup')
        first_feedbackset = group.feedbackset_set.first()
        mommy.make('devilry_group.FeedbackSet',
                   group=group,
                   deadline_datetime=ACTIVE_PERIOD_START)
        mommy.make('devilry_group.FeedbackSet',
                   group=group,
                   deadline_datetime=ACTIVE_PERIOD_START + timedelta(days=2))
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.first_feedbackset, first_feedbackset)

    def test_last_feedbackset(self):
        group = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=group,
                   deadline_datetime=ACTIVE_PERIOD_START)
        last_feedbackset = mommy.make('devilry_group.FeedbackSet',
                                      group=group,
                                      deadline_datetime=ACTIVE_PERIOD_START + timedelta(days=2))
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_feedbackset, last_feedbackset)

    def test_last_published_feedbackset_none(self):
        group = mommy.make('core.AssignmentGroup')
        mommy.make('devilry_group.FeedbackSet',
                   group=group,
                   deadline_datetime=ACTIVE_PERIOD_START)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_published_feedbackset, None)

    def test_last_published_feedbackset_simple(self):
        group = mommy.make('core.AssignmentGroup')
        last_published_feedbackset = mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            grading_published_datetime=ACTIVE_PERIOD_START,
            deadline_datetime=ACTIVE_PERIOD_START)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_published_feedbackset,
                         last_published_feedbackset)

    def test_last_published_feedbackset_multiple(self):
        group = mommy.make('core.AssignmentGroup')
        mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            grading_published_datetime=ACTIVE_PERIOD_START,
            deadline_datetime=ACTIVE_PERIOD_START)
        last_published_feedbackset = mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            grading_published_datetime=ACTIVE_PERIOD_START,
            deadline_datetime=ACTIVE_PERIOD_START + timedelta(days=2))
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_published_feedbackset,
                         last_published_feedbackset)

    def test_last_published_feedbackset_ignore_unpublished(self):
        group = mommy.make('core.AssignmentGroup')
        last_published_feedbackset = mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            grading_published_datetime=ACTIVE_PERIOD_START,
            deadline_datetime=ACTIVE_PERIOD_START)
        mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            deadline_datetime=ACTIVE_PERIOD_START + timedelta(days=2))
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_published_feedbackset,
                         last_published_feedbackset)

    def test_new_attempt_count(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.new_attempt_count, 0)
        mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            deadline_datetime=ACTIVE_PERIOD_START)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.new_attempt_count, 1)
        mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            deadline_datetime=ACTIVE_PERIOD_START + timedelta(days=2))
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.new_attempt_count, 2)


class TestAssignmentGroupCachedDataPublicTotalCommentCount(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_public_total_comment_count_none(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_comment_count, 0)

    def test_public_total_comment_count_simple(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=3)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_comment_count, 3)

    def test_public_total_comment_count_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_comment_count, 0)

    def test_public_total_comment_count_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_comment_count, 0)

    def test_public_total_comment_count_multiple_feedbacksets(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=2)
        feedbackset2 = mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            deadline_datetime=ACTIVE_PERIOD_START)
        mommy.make('devilry_group.GroupComment',
                   feedback_set=feedbackset2,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=4)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_comment_count, 6)

    def test_public_total_comment_count_delete_decrements_count(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        groupcomment1 = mommy.make(
            'devilry_group.GroupComment',
            feedback_set=feedbackset1,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make(
            'devilry_group.GroupComment',
            feedback_set=feedbackset1,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_comment_count, 2)
        groupcomment1.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_comment_count, 1)


class TestAssignmentGroupCachedDataPublicStudentCommentCount(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_public_student_comment_count_none(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 0)

    def test_public_student_comment_count_simple(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=3)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 3)

    def test_public_student_comment_count_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 0)

    def test_public_student_comment_count_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 0)

    def test_public_student_comment_count_ignore_user_role_examiner(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 0)

    def test_public_student_comment_count_ignore_user_role_admin(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 0)

    def test_public_student_comment_count_multiple_feedbacksets(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=2)
        feedbackset2 = mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            deadline_datetime=ACTIVE_PERIOD_START)
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset2,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=4)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 6)

    def test_public_student_comment_count_delete_decrements_count(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        groupcomment1 = mommy.make(
            'devilry_group.GroupComment',
            user_role=Comment.USER_ROLE_STUDENT,
            feedback_set=feedbackset1,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make(
            'devilry_group.GroupComment',
            user_role=Comment.USER_ROLE_STUDENT,
            feedback_set=feedbackset1,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 2)
        groupcomment1.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 1)


class TestAssignmentGroupCachedDataPublicExaminerCommentCount(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_public_examiner_comment_count_none(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 0)

    def test_public_examiner_comment_count_simple(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=3)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 3)

    def test_public_examiner_comment_count_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 0)

    def test_public_examiner_comment_count_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 0)

    def test_public_examiner_comment_count_ignore_user_role_student(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 0)

    def test_public_examiner_comment_count_ignore_user_role_admin(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 0)

    def test_public_examiner_comment_count_multiple_feedbacksets(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=2)
        feedbackset2 = mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            deadline_datetime=ACTIVE_PERIOD_START)
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset2,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=4)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 6)

    def test_public_examiner_comment_count_delete_decrements_count(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        groupcomment1 = mommy.make(
            'devilry_group.GroupComment',
            user_role=Comment.USER_ROLE_EXAMINER,
            feedback_set=feedbackset1,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make(
            'devilry_group.GroupComment',
            user_role=Comment.USER_ROLE_EXAMINER,
            feedback_set=feedbackset1,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 2)
        groupcomment1.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 1)


class TestAssignmentGroupCachedDataPublicAdminCommentCount(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_public_admin_comment_count_none(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 0)

    def test_public_admin_comment_count_simple(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=3)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 3)

    def test_public_admin_comment_count_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 0)

    def test_public_admin_comment_count_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 0)

    def test_public_admin_comment_count_ignore_user_role_student(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 0)

    def test_public_admin_comment_count_ignore_user_role_examiner(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 0)

    def test_public_admin_comment_count_multiple_feedbacksets(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=2)
        feedbackset2 = mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            deadline_datetime=ACTIVE_PERIOD_START)
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset2,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=4)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 6)

    def test_public_admin_comment_count_delete_decrements_count(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        groupcomment1 = mommy.make(
            'devilry_group.GroupComment',
            user_role=Comment.USER_ROLE_ADMIN,
            feedback_set=feedbackset1,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make(
            'devilry_group.GroupComment',
            user_role=Comment.USER_ROLE_ADMIN,
            feedback_set=feedbackset1,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 2)
        groupcomment1.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 1)


class TestAssignmentGroupCachedDataPublicTotalImageAnnotationCommentCount(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_public_total_imageannotationcomment_count_none(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_imageannotationcomment_count, 0)

    def test_public_total_imageannotationcomment_count_simple(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=3)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_imageannotationcomment_count, 3)

    def test_public_total_imageannotationcomment_count_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_imageannotationcomment_count, 0)

    def test_public_total_imageannotationcomment_count_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_imageannotationcomment_count, 0)

    def test_public_total_imageannotationcomment_count_multiple_feedbacksets(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=2)
        feedbackset2 = mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            deadline_datetime=ACTIVE_PERIOD_START)
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset2,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=4)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_imageannotationcomment_count, 6)

    def test_public_total_imageannotationcomment_count_delete_decrements_count(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        groupcomment1 = mommy.make(
            'devilry_group.ImageAnnotationComment',
            feedback_set=feedbackset1,
            visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make(
            'devilry_group.ImageAnnotationComment',
            feedback_set=feedbackset1,
            visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_imageannotationcomment_count, 2)
        groupcomment1.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_imageannotationcomment_count, 1)


class TestAssignmentGroupCachedDataPublicStudentImageAnnotationCommentCount(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_public_student_imageannotationcomment_count_none(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_imageannotationcomment_count, 0)

    def test_public_student_imageannotationcomment_count_simple(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=3)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_imageannotationcomment_count, 3)

    def test_public_student_imageannotationcomment_count_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_imageannotationcomment_count, 0)

    def test_public_student_imageannotationcomment_count_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_imageannotationcomment_count, 0)

    def test_public_student_imageannotationcomment_count_ignore_user_role_examiner(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_imageannotationcomment_count, 0)

    def test_public_student_imageannotationcomment_count_ignore_user_role_admin(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_imageannotationcomment_count, 0)

    def test_public_student_imageannotationcomment_count_multiple_feedbacksets(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=2)
        feedbackset2 = mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            deadline_datetime=ACTIVE_PERIOD_START)
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset2,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=4)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_imageannotationcomment_count, 6)

    def test_public_student_imageannotationcomment_count_delete_decrements_count(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        groupcomment1 = mommy.make(
            'devilry_group.ImageAnnotationComment',
            user_role=Comment.USER_ROLE_STUDENT,
            feedback_set=feedbackset1,
            visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make(
            'devilry_group.ImageAnnotationComment',
            user_role=Comment.USER_ROLE_STUDENT,
            feedback_set=feedbackset1,
            visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_imageannotationcomment_count, 2)
        groupcomment1.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_imageannotationcomment_count, 1)


class TestAssignmentGroupCachedDataPublicExaminerImageAnnotationCommentCount(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_public_examiner_imageannotationcomment_count_none(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_imageannotationcomment_count, 0)

    def test_public_examiner_imageannotationcomment_count_simple(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=3)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_imageannotationcomment_count, 3)

    def test_public_examiner_imageannotationcomment_count_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_imageannotationcomment_count, 0)

    def test_public_examiner_imageannotationcomment_count_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_imageannotationcomment_count, 0)

    def test_public_examiner_imageannotationcomment_count_ignore_user_role_student(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_imageannotationcomment_count, 0)

    def test_public_examiner_imageannotationcomment_count_ignore_user_role_admin(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_imageannotationcomment_count, 0)

    def test_public_examiner_imageannotationcomment_count_multiple_feedbacksets(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=2)
        feedbackset2 = mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            deadline_datetime=ACTIVE_PERIOD_START)
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset2,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=4)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_imageannotationcomment_count, 6)

    def test_public_examiner_imageannotationcomment_count_delete_decrements_count(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        groupcomment1 = mommy.make(
            'devilry_group.ImageAnnotationComment',
            user_role=Comment.USER_ROLE_EXAMINER,
            feedback_set=feedbackset1,
            visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make(
            'devilry_group.ImageAnnotationComment',
            user_role=Comment.USER_ROLE_EXAMINER,
            feedback_set=feedbackset1,
            visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_imageannotationcomment_count, 2)
        groupcomment1.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_imageannotationcomment_count, 1)


class TestAssignmentGroupCachedDataPublicAdminImageAnnotationCommentCount(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_public_admin_imageannotationcomment_count_none(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_imageannotationcomment_count, 0)

    def test_public_admin_imageannotationcomment_count_simple(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=3)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_imageannotationcomment_count, 3)

    def test_public_admin_imageannotationcomment_count_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_imageannotationcomment_count, 0)

    def test_public_admin_imageannotationcomment_count_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_imageannotationcomment_count, 0)

    def test_public_admin_imageannotationcomment_count_ignore_user_role_student(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_imageannotationcomment_count, 0)

    def test_public_admin_imageannotationcomment_count_ignore_user_role_examiner(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_imageannotationcomment_count, 0)

    def test_public_admin_imageannotationcomment_count_multiple_feedbacksets(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=2)
        feedbackset2 = mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            deadline_datetime=ACTIVE_PERIOD_START)
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset2,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=4)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_imageannotationcomment_count, 6)

    def test_public_admin_imageannotationcomment_count_delete_decrements_count(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        groupcomment1 = mommy.make(
            'devilry_group.ImageAnnotationComment',
            user_role=Comment.USER_ROLE_ADMIN,
            feedback_set=feedbackset1,
            visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make(
            'devilry_group.ImageAnnotationComment',
            user_role=Comment.USER_ROLE_ADMIN,
            feedback_set=feedbackset1,
            visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_imageannotationcomment_count, 2)
        groupcomment1.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_imageannotationcomment_count, 1)


class TestAssignmentGroupCachedDataPublicStudentFileUploadCount(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_public_student_file_upload_count_none(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_file_upload_count, 0)

    def test_public_student_file_upload_count_simple(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        comment = mommy.make(
            'devilry_group.GroupComment',
            user_role=Comment.USER_ROLE_STUDENT,
            feedback_set=feedbackset1,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_comment.CommentFile', comment=comment, _quantity=3)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_file_upload_count, 3)

    def test_public_student_file_upload_count_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        comment = mommy.make('devilry_group.GroupComment',
                             user_role=Comment.USER_ROLE_STUDENT,
                             feedback_set=feedbackset1,
                             visibility=GroupComment.VISIBILITY_PRIVATE)
        mommy.make('devilry_comment.CommentFile', comment=comment)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_file_upload_count, 0)

    def test_public_student_file_upload_count_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        comment = mommy.make('devilry_group.GroupComment',
                             user_role=Comment.USER_ROLE_STUDENT,
                             feedback_set=feedbackset1,
                             visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        mommy.make('devilry_comment.CommentFile', comment=comment)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_file_upload_count, 0)

    def test_public_student_file_upload_count_ignore_user_role_examiner(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        comment = mommy.make('devilry_group.GroupComment',
                             user_role=Comment.USER_ROLE_EXAMINER,
                             feedback_set=feedbackset1,
                             visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_comment.CommentFile', comment=comment)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_file_upload_count, 0)

    def test_public_student_file_upload_count_ignore_user_role_admin(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        comment = mommy.make('devilry_group.GroupComment',
                             user_role=Comment.USER_ROLE_ADMIN,
                             feedback_set=feedbackset1,
                             visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_comment.CommentFile', comment=comment)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_file_upload_count, 0)

    def test_public_student_file_upload_count_multiple_feedbacksets(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        comment1 = mommy.make('devilry_group.GroupComment',
                              user_role=Comment.USER_ROLE_STUDENT,
                              feedback_set=feedbackset1,
                              visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_comment.CommentFile', comment=comment1, _quantity=2)
        feedbackset2 = mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            deadline_datetime=ACTIVE_PERIOD_START)
        comment2 = mommy.make('devilry_group.GroupComment',
                              user_role=Comment.USER_ROLE_STUDENT,
                              feedback_set=feedbackset2,
                              visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_comment.CommentFile', comment=comment2, _quantity=4)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_file_upload_count, 6)

    def test_public_student_file_upload_count_delete_decrements_count(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        commentcomment = mommy.make(
            'devilry_group.GroupComment',
            user_role=Comment.USER_ROLE_STUDENT,
            feedback_set=feedbackset1,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        commentfile1 = mommy.make('devilry_comment.CommentFile', comment=commentcomment)
        mommy.make('devilry_comment.CommentFile', comment=commentcomment)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_file_upload_count, 2)
        commentfile1.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_file_upload_count, 1)
