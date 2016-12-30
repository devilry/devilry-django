from datetime import datetime, timedelta

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_comment.models import CommentFile
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_dbcache.models import AssignmentGroupCachedData
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group.models import FeedbackSet, GroupComment, ImageAnnotationComment
from django import test
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import connection
from django.utils import timezone
from model_mommy import mommy


class TestFeedbackSetTriggers(test.TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_create_feedbackset_sanity(self):
        group = mommy.make('core.AssignmentGroup')
        autocreated_feedbackset = group.feedbackset_set.first()
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=group)
        cached_data = AssignmentGroupCachedData.objects.get(group=feedbackset.group)
        self.assertEqual(autocreated_feedbackset, cached_data.first_feedbackset)
        self.assertEqual(feedbackset, cached_data.last_feedbackset)
        self.assertIsNone(cached_data.last_published_feedbackset)

    def test_create_published_feedbackset(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 grading_published_datetime=timezone.now())
        cached_data = AssignmentGroupCachedData.objects.get(group=feedbackset.group)
        self.assertEqual(feedbackset, cached_data.last_published_feedbackset)

    def test_update_feedbackset_to_published_sanity(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet', grading_published_datetime=None)
        feedbackset.grading_published_datetime = timezone.now()
        feedbackset.save()
        cached_data = AssignmentGroupCachedData.objects.get(group=feedbackset.group)
        self.assertEqual(feedbackset, cached_data.last_published_feedbackset)

    def test_update_feedbackset_to_unpublished_sanity(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet', grading_published_datetime=timezone.now())
        feedbackset.grading_published_datetime = None
        feedbackset.save()
        cached_data = AssignmentGroupCachedData.objects.get(group=feedbackset.group)
        self.assertIsNone(cached_data.last_published_feedbackset)


class TestAssignmentGroupTriggers(test.TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_create_group_creates_feedbackset_sanity(self):
        group = mommy.make('core.AssignmentGroup')
        autocreated_feedbackset = group.feedbackset_set.first()
        self.assertIsNotNone(autocreated_feedbackset)
        self.assertEqual(FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT, autocreated_feedbackset.feedbackset_type)

    def test_create_group_creates_feedbackset_created_datetime_in_correct_timezone(self):
        # NOTE: We add 60 sec to before and after, because Django and postgres servers
        #       can be a bit out of sync with each other, and the important thing here
        #       is that the timestamp is somewhat correct (not in the wrong timezone).
        before = timezone.now() - timedelta(seconds=60)
        group = mommy.make('core.AssignmentGroup')
        after = timezone.now() + timedelta(seconds=60)
        autocreated_feedbackset = group.feedbackset_set.first()
        self.assertTrue(autocreated_feedbackset.created_datetime >= before)
        self.assertTrue(autocreated_feedbackset.created_datetime <= after)


class TestGroupCommentTriggers(test.TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_create_groupcomment_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        mommy.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   user_role=GroupComment.USER_ROLE_ADMIN,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        self.assertEqual(3, testgroup.cached_data.public_total_comment_count)

    def test_delete_groupcomment_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        comment1 = mommy.make('devilry_group.GroupComment',
                              feedback_set=feedbackset,
                              comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                              user_role=GroupComment.USER_ROLE_STUDENT,
                              visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        comment2 = mommy.make('devilry_group.GroupComment',
                              feedback_set=feedbackset,
                              comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                              user_role=GroupComment.USER_ROLE_EXAMINER,
                              visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        comment3 = mommy.make('devilry_group.GroupComment',
                              feedback_set=feedbackset,
                              comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                              user_role=GroupComment.USER_ROLE_ADMIN,
                              visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        comment1.delete()
        comment2.delete()
        comment3.delete()
        self.assertEqual(0, testgroup.cached_data.public_total_comment_count)

    def test_create_groupcomment_student_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        mommy.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        self.assertEqual(1, testgroup.cached_data.public_student_comment_count)

    def test_delete_groupcomment_student_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        comment1 = mommy.make('devilry_group.GroupComment',
                              feedback_set=feedbackset,
                              comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                              user_role=GroupComment.USER_ROLE_STUDENT,
                              visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        comment1.delete()
        self.assertEqual(0, testgroup.cached_data.public_student_comment_count)

    def test_create_groupcomment_examiner_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        mommy.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   user_role=GroupComment.USER_ROLE_EXAMINER,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        self.assertEqual(1, testgroup.cached_data.public_examiner_comment_count)

    def test_delete_groupcomment_examiner_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        comment1 = mommy.make('devilry_group.GroupComment',
                              feedback_set=feedbackset,
                              comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                              user_role=GroupComment.USER_ROLE_EXAMINER,
                              visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        comment1.delete()
        self.assertEqual(0, testgroup.cached_data.public_examiner_comment_count)

    def test_create_groupcomment_admin_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        mommy.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   user_role=GroupComment.USER_ROLE_ADMIN,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        self.assertEqual(1, testgroup.cached_data.public_admin_comment_count)

    def test_delete_groupcomment_admin_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        comment1 = mommy.make('devilry_group.GroupComment',
                              feedback_set=feedbackset,
                              comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                              user_role=GroupComment.USER_ROLE_ADMIN,
                              visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        comment1.delete()
        self.assertEqual(0, testgroup.cached_data.public_admin_comment_count)

    def test_groupcomment_count_with_imageannotationcomment(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        mommy.make('devilry_comment.CommentFile',
                   comment=mommy.make('devilry_group.GroupComment',
                                      feedback_set=feedbackset,
                                      comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                      user_role=GroupComment.USER_ROLE_STUDENT,
                                      visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE))
        testcomment = mommy.make('devilry_group.ImageAnnotationComment',
                                 feedback_set=feedbackset,
                                 comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                                 user_role=ImageAnnotationComment.USER_ROLE_STUDENT,
                                 visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_comment.CommentFile', comment=testcomment)
        self.assertEqual(1, testgroup.cached_data.public_student_comment_count)
        self.assertEqual(1, testgroup.cached_data.public_student_imageannotationcomment_count)


class TestImageAnnotationCommentTriggers(test.TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_create_imageannotationcomment_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset,
                   comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                   user_role=ImageAnnotationComment.USER_ROLE_STUDENT,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset,
                   comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                   user_role=ImageAnnotationComment.USER_ROLE_EXAMINER,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset,
                   comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                   user_role=ImageAnnotationComment.USER_ROLE_ADMIN,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        self.assertEqual(3, testgroup.cached_data.public_total_imageannotationcomment_count)

    def test_delete_imageannotationcomment_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        comment1 = mommy.make('devilry_group.ImageAnnotationComment',
                              feedback_set=feedbackset,
                              comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                              user_role=ImageAnnotationComment.USER_ROLE_STUDENT,
                              visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        comment2 = mommy.make('devilry_group.ImageAnnotationComment',
                              feedback_set=feedbackset,
                              comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                              user_role=ImageAnnotationComment.USER_ROLE_EXAMINER,
                              visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        comment3 = mommy.make('devilry_group.ImageAnnotationComment',
                              feedback_set=feedbackset,
                              comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                              user_role=ImageAnnotationComment.USER_ROLE_ADMIN,
                              visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        comment1.delete()
        comment2.delete()
        comment3.delete()
        self.assertEqual(0, testgroup.cached_data.public_total_imageannotationcomment_count)

    def test_create_imageannotationcomment_student_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset,
                   comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                   user_role=ImageAnnotationComment.USER_ROLE_STUDENT,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        self.assertEqual(1, testgroup.cached_data.public_student_imageannotationcomment_count)

    def test_delete_imageannotationcomment_student_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        comment1 = mommy.make('devilry_group.ImageAnnotationComment',
                              feedback_set=feedbackset,
                              comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                              user_role=ImageAnnotationComment.USER_ROLE_STUDENT,
                              visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        comment1.delete()
        self.assertEqual(0, testgroup.cached_data.public_student_imageannotationcomment_count)

    def test_create_imageannotationcomment_examiner_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset,
                   comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                   user_role=ImageAnnotationComment.USER_ROLE_EXAMINER,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        self.assertEqual(1, testgroup.cached_data.public_examiner_imageannotationcomment_count)

    def test_delete_imageannotationcomment_examiner_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        comment1 = mommy.make('devilry_group.ImageAnnotationComment',
                              feedback_set=feedbackset,
                              comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                              user_role=ImageAnnotationComment.USER_ROLE_EXAMINER,
                              visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        comment1.delete()
        self.assertEqual(0, testgroup.cached_data.public_examiner_imageannotationcomment_count)

    def test_create_imageannotationcomment_admin_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=feedbackset,
                   comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                   user_role=ImageAnnotationComment.USER_ROLE_ADMIN,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        self.assertEqual(1, testgroup.cached_data.public_admin_imageannotationcomment_count)

    def test_delete_imageannotationcomment_admin_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        comment1 = mommy.make('devilry_group.ImageAnnotationComment',
                              feedback_set=feedbackset,
                              comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                              user_role=ImageAnnotationComment.USER_ROLE_ADMIN,
                              visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        comment1.delete()
        self.assertEqual(0, testgroup.cached_data.public_admin_imageannotationcomment_count)


class TestCommentFileTriggers(test.TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_create_commentfile_total_gives_correct_count(self):
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
        self.assertEqual(2, testgroup.cached_data.file_upload_count_total)

    def test_delete_commentfile_total_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup)
        testcomment1 = mommy.make('devilry_group.GroupComment',
                                  feedback_set=feedbackset,
                                  comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                  user_role=GroupComment.USER_ROLE_STUDENT,
                                  visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        commentfile1 = mommy.make('devilry_comment.CommentFile', comment=testcomment1)
        testcomment2 = mommy.make('devilry_group.GroupComment',
                                  feedback_set=feedbackset,
                                  comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                  user_role=GroupComment.USER_ROLE_EXAMINER,
                                  visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        commentfile2 = mommy.make('devilry_comment.CommentFile', comment=testcomment2)
        commentfile1.delete()
        commentfile2.delete()
        self.assertEqual(0, testgroup.cached_data.file_upload_count_total)

    def test_create_commentfile_student_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=feedbackset,
                                 comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                 user_role=GroupComment.USER_ROLE_STUDENT,
                                 visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_comment.CommentFile', comment=testcomment)
        self.assertEqual(1, testgroup.cached_data.file_upload_count_student)

    def test_delete_commentfile_student_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=feedbackset,
                                 comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                 user_role=GroupComment.USER_ROLE_STUDENT,
                                 visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment)
        commentfile.delete()
        self.assertEqual(0, testgroup.cached_data.file_upload_count_student)

    def test_create_commentfile_examiner_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=feedbackset,
                                 comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                 user_role=GroupComment.USER_ROLE_EXAMINER,
                                 visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_comment.CommentFile', comment=testcomment)
        self.assertEqual(1, testgroup.cached_data.file_upload_count_examiner)

    def test_delete_commentfile_examiner_gives_correct_count(self):
        testgroup = mommy.make('core.AssignmentGroup')
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=feedbackset,
                                 comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                 user_role=GroupComment.USER_ROLE_EXAMINER,
                                 visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment)
        commentfile.delete()
        self.assertEqual(0, testgroup.cached_data.file_upload_count_examiner)


class TestRecrateCacheData(test.TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_feedbackset_count(self):
        testgroup1 = mommy.make('core.AssignmentGroup')
        feedbackset1_1 = devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)

        testgroup2 = mommy.make('core.AssignmentGroup')
        feedbackset2_1 = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup2)

        testgroup3 = mommy.make('core.AssignmentGroup')
        feedbackset3_1 = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup3, is_last_in_group=None)
        feedbackset3_2 = devilry_group_mommy_factories.feedbackset_new_attempt_published(group=testgroup3)

        testgroup4 = mommy.make('core.AssignmentGroup')
        feedbackset4_1 = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup4, is_last_in_group=None)
        feedbackset4_2 = devilry_group_mommy_factories.feedbackset_new_attempt_unpublished(group=testgroup4)

        AssignmentGroupDbCacheCustomSql().recreate_data()

        testgroup1_ = AssignmentGroup.objects.get(id=testgroup1.id)
        testgroup2_ = AssignmentGroup.objects.get(id=testgroup2.id)
        testgroup3_ = AssignmentGroup.objects.get(id=testgroup3.id)
        testgroup4_ = AssignmentGroup.objects.get(id=testgroup4.id)

        self.assertEqual(testgroup1.cached_data.feedbackset_count, testgroup1_.cached_data.feedbackset_count)
        self.assertEqual(testgroup2.cached_data.feedbackset_count, testgroup2_.cached_data.feedbackset_count)
        self.assertEqual(testgroup3.cached_data.feedbackset_count, testgroup3_.cached_data.feedbackset_count)
        self.assertEqual(testgroup4.cached_data.feedbackset_count, testgroup4_.cached_data.feedbackset_count)


    def test_create_commentfile_total_gives_correct_count(self):
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

        testcomment3 = mommy.make('devilry_group.ImageAnnotationComment',
                              feedback_set=feedbackset,
                              comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                              user_role=ImageAnnotationComment.USER_ROLE_ADMIN,
                              visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        self.assertEqual(2, testgroup.cached_data.file_upload_count_total)

        feedbackset_count = testgroup.cached_data.feedbackset_count
        public_total_comment_count = testgroup.cached_data.public_total_comment_count
        public_total_imageannotationcomment_count = testgroup.cached_data.public_total_imageannotationcomment_count

        AssignmentGroupDbCacheCustomSql().recreate_data()

        testgroup = AssignmentGroup.objects.get(id=testgroup.id)
        self.assertEqual(feedbackset_count, testgroup.cached_data.feedbackset_count)
        self.assertEqual(public_total_comment_count, testgroup.cached_data.public_total_comment_count)
        self.assertEqual(public_total_imageannotationcomment_count,
                         testgroup.cached_data.public_total_imageannotationcomment_count)


class TimeExecution(object):
    def __init__(self, label):
        self.start_time = None
        self.label = label

    def __enter__(self):
        self.start_time = datetime.now()

    def __exit__(self, ttype, value, traceback):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        print
        print '{}: {}s'.format(self.label, duration)
        print


def _run_sql(sql):
    cursor = connection.cursor()
    cursor.execute(sql)


def _remove_triggers():
    _run_sql("""
        DROP TRIGGER IF EXISTS devilry_dbcache_on_assignmentgroup_insert_trigger
            ON core_assignmentgroup;
        DROP TRIGGER IF EXISTS devilry_dbcache_on_feedbackset_insert_or_update_trigger
            ON devilry_group_feedbackset;

        DROP TRIGGER IF EXISTS devilry_dbcache_on_group_imageannotationcomment_trigger
            ON devilry_group_imageannotationcomment;

        DROP TRIGGER IF EXISTS devilry_dbcache_on_group_change_trigger
            ON devilry_group_imageannotationcomment;
    """)


class TestBenchMarkAssignmentGroupFileUploadCountTrigger(test.TestCase):

    def setUp(self):
        _remove_triggers()

    def __create_distinct_comments(self, label):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=group)

        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer__user=mommy.make(settings.AUTH_USER_MODEL))

        mommy.make(GroupComment, user=examiner.relatedexaminer.user, feedback_set=feedbackset,
                   user_role=GroupComment.USER_ROLE_ADMIN)
        comment_student = mommy.make(GroupComment, user=examiner.relatedexaminer.user, feedback_set=feedbackset,
                                     user_role=GroupComment.USER_ROLE_STUDENT)
        comment_examiner = mommy.make(GroupComment, user=examiner.relatedexaminer.user, feedback_set=feedbackset,
                                      user_role=GroupComment.USER_ROLE_EXAMINER)

        count = 1000
        with TimeExecution('{} ({})'.format(label, count)):
            for x in range(count):
                student_file = mommy.make(CommentFile, comment=comment_student)
                student_file.file.save('testfile.txt', ContentFile('test'))
                examiner_file = mommy.make(CommentFile, comment=comment_examiner)
                examiner_file.file.save('testfile.txt', ContentFile('test'))
                # student_file.delete()

                # f or c in comments:
                #     c.save()

                # for c in comments:
                #     c.delete()
                #
                # cached_data = AssignmentGroupCachedData.objects.get(group=group)
                # print "feedbackset_count:", cached_data.feedbackset_count
                # print "public_total_comment_count:", cached_data.public_total_comment_count
                # print "public_student_comment_count:", cached_data.public_student_comment_count
                # print "public_examiner_comment_count:", cached_data.public_examiner_comment_count
                # print "public_admin_comment_count:", cached_data.public_admin_comment_count
                #
                #
                # print "file_upload_count_total:", cached_data.file_upload_count_total
                # print "file_upload_count_student:", cached_data.file_upload_count_student
                # print "file_upload_count_examiner:", cached_data.file_upload_count_examiner

    def test_create_in_distinct_groups_without_triggers(self):
        self.__create_distinct_comments('file upload: no triggers')

    def test_create_in_distinct_groups_with_triggers(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        self.__create_distinct_comments('file upload: with triggers')


class TestBenchMarkFeedbackSetTrigger(test.TestCase):

    def setUp(self):
        _remove_triggers()

    def __create_in_distinct_groups_feedbacksets(self, label):
        count = 10000
        assignment = mommy.make('core.Assignment')
        created_by = mommy.make(settings.AUTH_USER_MODEL)

        groups = []
        for x in range(count):
            groups.append(mommy.prepare('core.AssignmentGroup', parentnode=assignment))
        AssignmentGroup.objects.bulk_create(groups)

        feedbacksets = []
        for group in AssignmentGroup.objects.filter(parentnode=assignment):
            feedbackset = mommy.prepare(FeedbackSet, group=group, created_by=created_by, is_last_in_group=None)
            feedbacksets.append(feedbackset)

        with TimeExecution('{} ({})'.format(label, count)):
            FeedbackSet.objects.bulk_create(feedbacksets)

    def test_create_feedbacksets_in_distinct_groups_without_triggers(self):
        self.__create_in_distinct_groups_feedbacksets('feedbacksets distinct groups: no triggers')

    def test_create_feedbacksets_in_distinct_groups_with_triggers(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        self.__create_in_distinct_groups_feedbacksets('feedbacksets distinct groups: with triggers')

    def __create_in_same_group_feedbacksets(self, label):
        count = 1000
        assignment = mommy.make('core.Assignment')
        created_by = mommy.make(settings.AUTH_USER_MODEL)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)

        feedbacksets = []
        for x in range(count):
            feedbackset = mommy.prepare(FeedbackSet, group=group, created_by=created_by, is_last_in_group=None)
            feedbacksets.append(feedbackset)

        with TimeExecution('{} ({})'.format(label, count)):
            FeedbackSet.objects.bulk_create(feedbacksets)

    def test_create_feedbacksets_in_same_group_without_triggers(self):
        self.__create_in_same_group_feedbacksets('feedbacksets same group: no triggers')

    def test_create_feedbacksets_in_same_group_with_triggers(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        # This should have some overhead because we need to UPDATE the AssignmentGroupCachedData
        # for each INSERT
        self.__create_in_same_group_feedbacksets('feedbacksets same group: with triggers')


class TestBenchMarkAssignmentGroupTrigger(test.TestCase):
    def setUp(self):
        _remove_triggers()

    def __create_distinct_groups(self, label):
        count = 10000
        assignment = mommy.make('core.Assignment')
        groups = []
        for x in range(count):
            groups.append(mommy.prepare('core.AssignmentGroup', parentnode=assignment))

        with TimeExecution('{} ({})'.format(label, count)):
            AssignmentGroup.objects.bulk_create(groups)

    def test_create_in_distinct_groups_without_triggers(self):
        self.__create_distinct_groups('assignment groups: no triggers')

    def test_create_in_distinct_groups_with_triggers(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        self.__create_distinct_groups('assignment groups: with triggers')


class TestBenchMarkAssignmentGroupCommentCountTrigger(test.TestCase):
    def setUp(self):
        _remove_triggers()

    def __create_distinct_comments(self, label):
        assignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=group)

        examiner = mommy.make('core.Examiner',
                              assignmentgroup=group,
                              relatedexaminer__user=mommy.make(settings.AUTH_USER_MODEL))

        count = 100
        comments = []
        for x in range(count):
            comments.append(mommy.prepare(GroupComment, user=examiner.relatedexaminer.user, feedback_set=feedbackset,
                                          user_role=GroupComment.USER_ROLE_ADMIN))
            comments.append(mommy.prepare(GroupComment, user=examiner.relatedexaminer.user, feedback_set=feedbackset,
                                          user_role=GroupComment.USER_ROLE_STUDENT))
            comments.append(mommy.prepare(GroupComment, user=examiner.relatedexaminer.user, feedback_set=feedbackset,
                                          user_role=GroupComment.USER_ROLE_EXAMINER))

        with TimeExecution('{} ({})'.format(label, count)):
            for c in comments:
                c.save()

                # for c in comments:
                #    c.delete()
                #
        return group

    def test_create_in_distinct_groups_without_triggers(self):
        self.__create_distinct_comments('assignment groups comments: no triggers')

    def test_create_in_distinct_groups_with_triggers(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        group = self.__create_distinct_comments('assignment groups comments: with triggers')
        cached_data = AssignmentGroupCachedData.objects.get(group=group)
        print "feedbackset_count:", cached_data.feedbackset_count
        print "public_total_comment_count:", cached_data.public_total_comment_count
        print "public_student_comment_count:", cached_data.public_student_comment_count
        print "public_examiner_comment_count:", cached_data.public_examiner_comment_count
        print "public_admin_comment_count:", cached_data.public_admin_comment_count
