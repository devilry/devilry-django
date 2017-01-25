from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from devilry.devilry_group import models as group_models


class TestGroupCommentModel(TestCase):

    def test_groupcomment_part_of_grading_default_false(self):
        test_comment = mommy.make('devilry_group.GroupComment')
        self.assertEquals(False, test_comment.part_of_grading)

    def test_groupcomment_visibility_default_visible_to_everyone(self):
        test_comment = mommy.make('devilry_group.GroupComment')
        self.assertEquals(group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE, test_comment.visibility)

    def test_groupcomment_get_published_datetime_part_of_grading(self):
        time = timezone.now()
        test_feedbackset = mommy.make('devilry_group.FeedbackSet',
                                      grading_published_datetime=time)
        test_comment = mommy.make('devilry_group.GroupComment',
                                  feedback_set=test_feedbackset,
                                  part_of_grading=True)
        self.assertEquals(test_feedbackset.grading_published_datetime, test_comment.get_published_datetime())

    def test_groupcomment_get_published_datetime_not_part_of_grading(self):
        test_feedbackset = mommy.make('devilry_group.FeedbackSet',
                                      grading_published_datetime=timezone.now())
        test_comment = mommy.make('devilry_group.GroupComment',
                                  published_datetime=timezone.now(),
                                  feedback_set=test_feedbackset)
        self.assertEquals(test_comment.published_datetime, test_comment.get_published_datetime())

    def test_groupcomment_publish_draft(self):
        test_draftcomment = mommy.make('devilry_group.GroupComment',
                                       published_datetime=timezone.now(),
                                       part_of_grading=True,
                                       visibility=group_models.GroupComment.VISIBILITY_PRIVATE)
        time = timezone.now()
        test_draftcomment.publish_draft(time)
        self.assertTrue(test_draftcomment.part_of_grading)
        self.assertEquals(test_draftcomment.visibility, group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        self.assertEquals(test_draftcomment.published_datetime, time)

    def test_groupcomment_feedback_set(self):
        test_feedbackset = mommy.make('devilry_group.FeedbackSet')
        test_comment = mommy.make('devilry_group.GroupComment', feedback_set=test_feedbackset)
        self.assertEquals(test_comment.feedback_set, test_feedbackset)

    def test_clean_groupcomment_student_private_comment(self):
        test_comment = mommy.prepare('devilry_group.GroupComment',
                                     user_role=group_models.GroupComment.USER_ROLE_STUDENT,
                                     visibility=group_models.GroupComment.VISIBILITY_PRIVATE)
        with self.assertRaisesMessage(ValidationError,
                                      'A student comment is always visible to everyone'):
            test_comment.clean()

    def test_clean_groupcomment_examiner_non_draft_is_private(self):
        test_comment = mommy.prepare('devilry_group.GroupComment',
                                     user_role=group_models.GroupComment.USER_ROLE_EXAMINER,
                                     visibility=group_models.GroupComment.VISIBILITY_PRIVATE)
        with self.assertRaisesMessage(ValidationError,
                                      'A examiner comment can only be private if part of grading.'):
            test_comment.clean()
