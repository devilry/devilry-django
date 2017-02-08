from datetime import timedelta

from django import test
from model_mommy import mommy

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Candidate
from devilry.apps.core.models import Examiner
from devilry.apps.core.mommy_recipes import ACTIVE_PERIOD_START
from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_comment.models import Comment
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_dbcache.models import AssignmentGroupCachedData
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group.models import GroupComment, ImageAnnotationComment, FeedbackSet


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
        assignment = mommy.make('core.Assignment', first_deadline=ACTIVE_PERIOD_START - timedelta(days=2))
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
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
        assignment = mommy.make('core.Assignment', first_deadline=ACTIVE_PERIOD_START - timedelta(days=2))
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
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


class TestAssignmentGroupCachedDataExaminerCount(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_none(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.examiner_count, 0)

    def test_examiner_simple(self):
        group = mommy.make('core.AssignmentGroup')
        core_mommy.examiner(group=group)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.examiner_count, 1)

    def test_examiner_multiple(self):
        group = mommy.make('core.AssignmentGroup')
        core_mommy.examiner(group=group)
        core_mommy.examiner(group=group)
        core_mommy.examiner(group=group)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.examiner_count, 3)

    def test_examiner_delete_decrements_count(self):
        group = mommy.make('core.AssignmentGroup')
        core_mommy.examiner(group=group)
        examiner = core_mommy.examiner(group=group)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.examiner_count, 2)
        examiner.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.examiner_count, 1)

    def test_examiner_count_when_examiner_moved(self):
        group1 = mommy.make('core.AssignmentGroup')
        group2 = mommy.make('core.AssignmentGroup')
        core_mommy.examiner(group=group1)
        core_mommy.examiner(group=group2)
        examiner = core_mommy.examiner(group=group1)
        core_mommy.examiner(group=group2)
        self.assertEqual(group1.cached_data.examiner_count, 2)
        self.assertEqual(group2.cached_data.examiner_count, 2)
        examiner.assignmentgroup = group2
        examiner.save()
        group1.cached_data.refresh_from_db()
        self.assertEqual(group1.cached_data.examiner_count, 1)
        group2.cached_data.refresh_from_db()
        self.assertEqual(group2.cached_data.examiner_count, 3)


class TestAssignmentGroupCachedDataCandidateCount(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_none(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.candidate_count, 0)

    def test_examiner_simple(self):
        group = mommy.make('core.AssignmentGroup')
        core_mommy.candidate(group=group)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.candidate_count, 1)

    def test_candidate_multiple(self):
        group = mommy.make('core.AssignmentGroup')
        core_mommy.candidate(group=group)
        core_mommy.candidate(group=group)
        core_mommy.candidate(group=group)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.candidate_count, 3)

    def test_candidate_delete_decrements_count(self):
        group = mommy.make('core.AssignmentGroup')
        core_mommy.candidate(group=group)
        candidate = core_mommy.candidate(group=group)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.candidate_count, 2)
        candidate.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.candidate_count, 1)

    def test_num_queries(self):
        group = mommy.make('core.AssignmentGroup')
        core_mommy.candidate(group=group)
        core_mommy.examiner(group=group)
        with self.assertNumQueries(20):
            group.delete()

    def test_candidate_count_when_candidate_moved(self):
        group1 = mommy.make('core.AssignmentGroup')
        group2 = mommy.make('core.AssignmentGroup')
        core_mommy.candidate(group=group1)
        core_mommy.candidate(group=group2)
        candidate = core_mommy.candidate(group=group1)
        core_mommy.candidate(group=group2)
        self.assertEqual(group1.cached_data.candidate_count, 2)
        self.assertEqual(group2.cached_data.candidate_count, 2)
        candidate.assignment_group = group2
        candidate.save()
        group1.cached_data.refresh_from_db()
        self.assertEqual(group1.cached_data.candidate_count, 1)
        group2.cached_data.refresh_from_db()
        self.assertEqual(group2.cached_data.candidate_count, 3)


class TestAssignmentGroupCachedDataPublicTotalCommentCount(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_none(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_comment_count, 0)

    def test_groupcomment_simple(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=3)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_comment_count, 3)

    def test_groupcomment_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_comment_count, 0)

    def test_groupcomment_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_comment_count, 0)

    def test_groupcomment_multiple_feedbacksets(self):
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

    def test_groupcomment_delete_decrements_count(self):
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

    def test_imageannotationcomment_simple(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=3)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_comment_count, 3)

    def test_imageannotationcomment_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_comment_count, 0)

    def test_imageannotationcomment_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_comment_count, 0)

    def test_imageannotationcomment_multiple_feedbacksets(self):
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
        self.assertEqual(group.cached_data.public_total_comment_count, 6)

    def test_imageannotationcomment_delete_decrements_count(self):
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
        self.assertEqual(group.cached_data.public_total_comment_count, 2)
        groupcomment1.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_total_comment_count, 1)


class TestAssignmentGroupCachedDataPublicStudentCommentCount(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_none(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 0)

    def test_groupcomment_simple(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=3)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 3)

    def test_groupcomment_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 0)

    def test_groupcomment_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 0)

    def test_groupcomment_ignore_user_role_examiner(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 0)

    def test_groupcomment_ignore_user_role_admin(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 0)

    def test_groupcomment_multiple_feedbacksets(self):
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

    def test_groupcomment_delete_decrements_count(self):
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

    def test_imageannotationcomment_simple(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=3)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 3)

    def test_imageannotationcomment_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 0)

    def test_imageannotationcomment_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 0)

    def test_imageannotationcomment_ignore_user_role_examiner(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 0)

    def test_imageannotationcomment_ignore_user_role_admin(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 0)

    def test_imageannotationcomment_multiple_feedbacksets(self):
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
        self.assertEqual(group.cached_data.public_student_comment_count, 6)

    def test_imageannotationcomment_delete_decrements_count(self):
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
        self.assertEqual(group.cached_data.public_student_comment_count, 2)
        groupcomment1.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_student_comment_count, 1)


class TestAssignmentGroupCachedDataPublicExaminerCommentCount(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_none(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 0)

    def test_groupcomment_simple(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=3)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 3)

    def test_groupcomment_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 0)

    def test_groupcomment_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 0)

    def test_groupcomment_ignore_user_role_student(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 0)

    def test_groupcomment_ignore_user_role_admin(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 0)

    def test_groupcomment_multiple_feedbacksets(self):
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

    def test_groupcomment_delete_decrements_count(self):
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

    def test_imageannotationcomment_simple(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=3)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 3)

    def test_imageannotationcomment_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 0)

    def test_imageannotationcomment_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 0)

    def test_imageannotationcomment_ignore_user_role_student(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 0)

    def test_imageannotationcomment_ignore_user_role_admin(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 0)

    def test_imageannotationcomment_multiple_feedbacksets(self):
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
        self.assertEqual(group.cached_data.public_examiner_comment_count, 6)

    def test_imageannotationcomment_delete_decrements_count(self):
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
        self.assertEqual(group.cached_data.public_examiner_comment_count, 2)
        groupcomment1.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_examiner_comment_count, 1)


class TestAssignmentGroupCachedDataPublicAdminCommentCount(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_none(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 0)

    def test_groupcomment_simple(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=3)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 3)

    def test_groupcomment_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 0)

    def test_groupcomment_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 0)

    def test_groupcomment_ignore_user_role_student(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 0)

    def test_groupcomment_ignore_user_role_examiner(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 0)

    def test_groupcomment_multiple_feedbacksets(self):
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

    def test_groupcomment_delete_decrements_count(self):
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

    def test_imageannotationcomment_simple(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   _quantity=3)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 3)

    def test_imageannotationcomment_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 0)

    def test_imageannotationcomment_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 0)

    def test_imageannotationcomment_ignore_user_role_student(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 0)

    def test_imageannotationcomment_ignore_user_role_examiner(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 0)

    def test_imageannotationcomment_multiple_feedbacksets(self):
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
        self.assertEqual(group.cached_data.public_admin_comment_count, 6)

    def test_imageannotationcomment_delete_decrements_count(self):
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
        self.assertEqual(group.cached_data.public_admin_comment_count, 2)
        groupcomment1.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.public_admin_comment_count, 1)


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


class TestAssignmentGroupCachedDataLastPublicCommentByStudentDatetime(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_none(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_student_datetime, None)

    def test_groupcomment_single(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        comment = mommy.make('devilry_group.GroupComment',
                             user_role=Comment.USER_ROLE_STUDENT,
                             feedback_set=feedbackset1,
                             visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_student_datetime,
                         comment.published_datetime)

    def test_groupcomment_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_student_datetime, None)

    def test_groupcomment_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_student_datetime, None)

    def test_groupcomment_ignore_user_role_examiner(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_student_datetime, None)

    def test_groupcomment_ignore_user_role_admin(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_student_datetime, None)

    def test_groupcomment_multiple_feedbacksets(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        feedbackset2 = mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            deadline_datetime=ACTIVE_PERIOD_START)
        comment2 = mommy.make('devilry_group.GroupComment',
                              user_role=Comment.USER_ROLE_STUDENT,
                              feedback_set=feedbackset2,
                              visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_student_datetime,
                         comment2.published_datetime)

    def test_groupcomment_delete_updates_datetime(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        groupcomment1 = mommy.make(
            'devilry_group.GroupComment',
            user_role=Comment.USER_ROLE_STUDENT,
            feedback_set=feedbackset1,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        groupcomment2 = mommy.make(
            'devilry_group.GroupComment',
            user_role=Comment.USER_ROLE_STUDENT,
            feedback_set=feedbackset1,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_student_datetime,
                         groupcomment2.published_datetime)
        groupcomment2.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_student_datetime,
                         groupcomment1.published_datetime)

    def test_imageannotationcomment_single(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        comment = mommy.make('devilry_group.ImageAnnotationComment',
                             user_role=Comment.USER_ROLE_STUDENT,
                             feedback_set=feedbackset1,
                             visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_student_datetime,
                         comment.published_datetime)

    def test_imageannotationcomment_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_student_datetime, None)

    def test_imageannotationcomment_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_student_datetime, None)

    def test_imageannotationcomment_ignore_user_role_examiner(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_student_datetime, None)

    def test_imageannotationcomment_ignore_user_role_admin(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_student_datetime, None)

    def test_imageannotationcomment_multiple_feedbacksets(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        feedbackset2 = mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            deadline_datetime=ACTIVE_PERIOD_START)
        comment2 = mommy.make('devilry_group.ImageAnnotationComment',
                              user_role=Comment.USER_ROLE_STUDENT,
                              feedback_set=feedbackset2,
                              visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_student_datetime,
                         comment2.published_datetime)

    def test_imageannotationcomment_delete_updates_datetime(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        comment1 = mommy.make(
            'devilry_group.ImageAnnotationComment',
            user_role=Comment.USER_ROLE_STUDENT,
            feedback_set=feedbackset1,
            visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        comment2 = mommy.make(
            'devilry_group.ImageAnnotationComment',
            user_role=Comment.USER_ROLE_STUDENT,
            feedback_set=feedbackset1,
            visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_student_datetime,
                         comment2.published_datetime)
        comment2.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_student_datetime,
                         comment1.published_datetime)


class TestAssignmentGroupCachedDataLastPublicCommentByExaminerDatetime(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_none(self):
        group = mommy.make('core.AssignmentGroup')
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_examiner_datetime, None)

    def test_groupcomment_single(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        comment = mommy.make('devilry_group.GroupComment',
                             user_role=Comment.USER_ROLE_EXAMINER,
                             feedback_set=feedbackset1,
                             visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_examiner_datetime,
                         comment.published_datetime)

    def test_groupcomment_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_examiner_datetime, None)

    def test_groupcomment_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_examiner_datetime, None)

    def test_groupcomment_ignore_user_role_student(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_examiner_datetime, None)

    def test_groupcomment_ignore_user_role_admin(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_examiner_datetime, None)

    def test_groupcomment_multiple_feedbacksets(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.GroupComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        feedbackset2 = mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            deadline_datetime=ACTIVE_PERIOD_START)
        comment2 = mommy.make('devilry_group.GroupComment',
                              user_role=Comment.USER_ROLE_EXAMINER,
                              feedback_set=feedbackset2,
                              visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_examiner_datetime,
                         comment2.published_datetime)

    def test_groupcomment_delete_updates_datetime(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        groupcomment1 = mommy.make(
            'devilry_group.GroupComment',
            user_role=Comment.USER_ROLE_EXAMINER,
            feedback_set=feedbackset1,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        groupcomment2 = mommy.make(
            'devilry_group.GroupComment',
            user_role=Comment.USER_ROLE_EXAMINER,
            feedback_set=feedbackset1,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_examiner_datetime,
                         groupcomment2.published_datetime)
        groupcomment2.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_examiner_datetime,
                         groupcomment1.published_datetime)

    def test_imageannotationcomment_single(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        comment = mommy.make('devilry_group.ImageAnnotationComment',
                             user_role=Comment.USER_ROLE_EXAMINER,
                             feedback_set=feedbackset1,
                             visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_examiner_datetime,
                         comment.published_datetime)

    def test_imageannotationcomment_ignore_private(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_examiner_datetime, None)

    def test_imageannotationcomment_ignore_visible_to_examiners_and_admins(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_examiner_datetime, None)

    def test_imageannotationcomment_ignore_user_role_student(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_STUDENT,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_examiner_datetime, None)

    def test_imageannotationcomment_ignore_user_role_admin(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_ADMIN,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_examiner_datetime, None)

    def test_imageannotationcomment_multiple_feedbacksets(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        mommy.make('devilry_group.ImageAnnotationComment',
                   user_role=Comment.USER_ROLE_EXAMINER,
                   feedback_set=feedbackset1,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        feedbackset2 = mommy.make(
            'devilry_group.FeedbackSet',
            group=group,
            deadline_datetime=ACTIVE_PERIOD_START)
        comment2 = mommy.make('devilry_group.ImageAnnotationComment',
                              user_role=Comment.USER_ROLE_EXAMINER,
                              feedback_set=feedbackset2,
                              visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_examiner_datetime,
                         comment2.published_datetime)

    def test_imageannotationcomment_delete_updates_datetime(self):
        group = mommy.make('core.AssignmentGroup')
        feedbackset1 = group.feedbackset_set.first()
        comment1 = mommy.make(
            'devilry_group.ImageAnnotationComment',
            user_role=Comment.USER_ROLE_EXAMINER,
            feedback_set=feedbackset1,
            visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        comment2 = mommy.make(
            'devilry_group.ImageAnnotationComment',
            user_role=Comment.USER_ROLE_EXAMINER,
            feedback_set=feedbackset1,
            visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_examiner_datetime,
                         comment2.published_datetime)
        comment2.delete()
        group.cached_data.refresh_from_db()
        self.assertEqual(group.cached_data.last_public_comment_by_examiner_datetime,
                         comment1.published_datetime)


class TestRecrateCacheData(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_new_attempt_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup)
        devilry_group_mommy_factories.feedbackset_new_attempt_published(group=testgroup)
        devilry_group_mommy_factories.feedbackset_new_attempt_unpublished(group=testgroup)
        testgroup.cached_data.refresh_from_db()
        self.assertEqual(testgroup.cached_data.new_attempt_count, 2)
        AssignmentGroupDbCacheCustomSql().recreate_data()
        testgroup = AssignmentGroup.objects.get(id=testgroup.id)
        testgroup.cached_data.refresh_from_db()
        self.assertEqual(testgroup.cached_data.new_attempt_count, 2)

    def test_public_total_comment_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup)
        testcomment1 = mommy.make('devilry_group.GroupComment',
                                  feedback_set=feedbackset,
                                  comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                  user_role=GroupComment.USER_ROLE_STUDENT,
                                  visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_comment.CommentFile', comment=testcomment1)
        testcomment2 = mommy.make('devilry_group.GroupComment',
                                  feedback_set=feedbackset,
                                  comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                  user_role=GroupComment.USER_ROLE_EXAMINER,
                                  visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_comment.CommentFile', comment=testcomment2)
        testgroup.cached_data.refresh_from_db()
        self.assertEqual(testgroup.cached_data.public_total_comment_count, 2)
        AssignmentGroupDbCacheCustomSql().recreate_data()
        testgroup = AssignmentGroup.objects.get(id=testgroup.id)
        self.assertEqual(testgroup.cached_data.public_total_comment_count, 2)


class TestAssignmentGroupDelete(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_delete_cached_data(self):
        testgroup = mommy.make('core.AssignmentGroup')
        cached_data_id = testgroup.cached_data.id
        core_mommy.examiner(group=testgroup)
        core_mommy.candidate(group=testgroup)
        testgroup.delete()
        self.assertFalse(AssignmentGroupCachedData.objects.filter(id=cached_data_id).exists())

    def test_delete_with_candidates_examiners_feedbacksets(self):
        testgroup = mommy.make('core.AssignmentGroup')
        examiner = core_mommy.examiner(group=testgroup)
        candidate = core_mommy.candidate(group=testgroup)
        feedbackset1 = group_mommy.feedbackset_first_attempt_published(group=testgroup)
        feedbackset2 = group_mommy.feedbackset_new_attempt_published(group=testgroup)
        feedbackset3 = group_mommy.feedbackset_new_attempt_unpublished(group=testgroup)
        testgroup.delete()
        self.assertFalse(AssignmentGroup.objects.filter(id=testgroup.id).exists())
        self.assertFalse(Examiner.objects.filter(id=examiner.id).exists())
        self.assertFalse(Candidate.objects.filter(id=candidate.id).exists())
        self.assertFalse(FeedbackSet.objects.filter(id=feedbackset1.id).exists())
        self.assertFalse(FeedbackSet.objects.filter(id=feedbackset2.id).exists())
        self.assertFalse(FeedbackSet.objects.filter(id=feedbackset3.id).exists())

    def test_delete_num_queries(self):
        testgroup = mommy.make('core.AssignmentGroup')
        core_mommy.examiner(group=testgroup)
        core_mommy.candidate(group=testgroup)
        group_mommy.feedbackset_first_attempt_published(group=testgroup)
        group_mommy.feedbackset_new_attempt_published(group=testgroup)
        group_mommy.feedbackset_new_attempt_unpublished(group=testgroup)
        with self.assertNumQueries(20):
            testgroup.delete()
