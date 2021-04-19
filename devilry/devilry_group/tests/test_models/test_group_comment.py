from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase
from django.utils import timezone
from model_bakery import baker

from devilry.apps.core import models as core_models
from devilry.devilry_group import models as group_models
from devilry.devilry_comment import models as comment_models
from devilry.devilry_group.models import GroupCommentEditHistory


class TestGroupCommentModel(TestCase):
    def test_groupcomment_part_of_grading_default_false(self):
        test_comment = baker.make('devilry_group.GroupComment',
                                  feedback_set__group__parentnode__parentnode=baker.make_recipe(
                                      'devilry.apps.core.period_active'))
        self.assertEqual(False, test_comment.part_of_grading)

    def test_groupcomment_visibility_default_visible_to_everyone(self):
        test_comment = baker.make('devilry_group.GroupComment',
                                  feedback_set__group__parentnode__parentnode=baker.make_recipe(
                                      'devilry.apps.core.period_active'))
        self.assertEqual(group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE, test_comment.visibility)

    def test_groupcomment_get_published_datetime_part_of_grading(self):
        time = timezone.now()
        test_feedbackset = baker.make('devilry_group.FeedbackSet',
                                      grading_published_datetime=time)
        test_comment = baker.make('devilry_group.GroupComment',
                                  feedback_set=test_feedbackset,
                                  part_of_grading=True,
                                  feedback_set__group__parentnode__parentnode=baker.make_recipe(
                                      'devilry.apps.core.period_active'))
        self.assertEqual(test_feedbackset.grading_published_datetime, test_comment.get_published_datetime())

    def test_groupcomment_get_published_datetime_not_part_of_grading(self):
        test_feedbackset = baker.make('devilry_group.FeedbackSet',
                                      grading_published_datetime=timezone.now(),
                                      group__parentnode__parentnode=baker.make_recipe(
                                          'devilry.apps.core.period_active'))
        test_comment = baker.make('devilry_group.GroupComment',
                                  published_datetime=timezone.now(),
                                  feedback_set=test_feedbackset)
        self.assertEqual(test_comment.published_datetime, test_comment.get_published_datetime())

    def test_groupcomment_publish_draft(self):
        test_draftcomment = baker.make('devilry_group.GroupComment',
                                       published_datetime=timezone.now(),
                                       part_of_grading=True,
                                       visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                                       feedback_set__group__parentnode__parentnode=baker.make_recipe(
                                           'devilry.apps.core.period_active'))
        time = timezone.now()
        test_draftcomment.publish_draft(time)
        self.assertTrue(test_draftcomment.part_of_grading)
        self.assertEqual(test_draftcomment.visibility, group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        self.assertEqual(test_draftcomment.published_datetime, time)

    def test_groupcomment_feedback_set(self):
        test_feedbackset = baker.make('devilry_group.FeedbackSet',
                                      group__parentnode__parentnode=baker.make_recipe(
                                          'devilry.apps.core.period_active'))
        test_comment = baker.make('devilry_group.GroupComment', feedback_set=test_feedbackset)
        self.assertEqual(test_comment.feedback_set, test_feedbackset)

    def test_clean_groupcomment_student_private_comment(self):
        test_comment = baker.prepare('devilry_group.GroupComment',
                                     user_role=group_models.GroupComment.USER_ROLE_STUDENT,
                                     visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                                     feedback_set__group__parentnode__parentnode=baker.make_recipe(
                                         'devilry.apps.core.period_active'))
        with self.assertRaisesMessage(ValidationError,
                                      'A student comment is always visible to everyone'):
            test_comment.clean()

    def test_clean_groupcomment_examiner_non_draft_is_private(self):
        test_comment = baker.prepare('devilry_group.GroupComment',
                                     user_role=group_models.GroupComment.USER_ROLE_EXAMINER,
                                     visibility=group_models.GroupComment.VISIBILITY_PRIVATE,
                                     feedback_set__group__parentnode__parentnode=baker.make_recipe(
                                         'devilry.apps.core.period_active'))
        with self.assertRaisesMessage(ValidationError,
                                      'A examiner comment can only be private if part of grading.'):
            test_comment.clean()

    def __make_assignment(self, first_deadline, deadline_handling=core_models.Assignment.DEADLINEHANDLING_SOFT):
        test_assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        test_assignment.first_deadline = first_deadline
        test_assignment.deadline_handling = deadline_handling
        return test_assignment

    def test_clean_student_comment_assignment_deadline_hard_expired(self):
        test_assignment = self.__make_assignment(
            first_deadline=timezone.now() - timezone.timedelta(days=1),
            deadline_handling=core_models.Assignment.DEADLINEHANDLING_HARD)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group__parentnode=test_assignment)
        test_comment = baker.prepare('devilry_group.GroupComment',
                                     feedback_set=test_feedbackset,
                                     user_role=group_models.GroupComment.USER_ROLE_STUDENT)
        with self.assertRaisesMessage(ValidationError, 'Hard deadlines are enabled for this assignment. '
                                                       'File upload and commenting is disabled.'):
            test_comment.clean()

    def test_can_student_comment_assignment_deadline_soft_expired(self):
        test_assignment = self.__make_assignment(
            first_deadline=timezone.now() - timezone.timedelta(days=1),
            deadline_handling=core_models.Assignment.DEADLINEHANDLING_SOFT)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group__parentnode=test_assignment)
        test_comment = baker.prepare('devilry_group.GroupComment',
                                     feedback_set=test_feedbackset,
                                     user_role=group_models.GroupComment.USER_ROLE_STUDENT)
        test_comment.clean()

    def test_clean_examiner_comment_assignment_deadline_hard_expired_no_exception_raised(self):
        test_assignment = self.__make_assignment(
            first_deadline=timezone.now() - timezone.timedelta(days=1),
            deadline_handling=core_models.Assignment.DEADLINEHANDLING_HARD)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group__parentnode=test_assignment)
        test_comment = baker.prepare('devilry_group.GroupComment',
                                     feedback_set=test_feedbackset,
                                     user_role=group_models.GroupComment.USER_ROLE_EXAMINER)
        test_comment.clean()

    def test_clean_admin_comment_assignment_deadline_hard_expired_no_exception_raised(self):
        test_assignment = self.__make_assignment(
            first_deadline=timezone.now() - timezone.timedelta(days=1),
            deadline_handling=core_models.Assignment.DEADLINEHANDLING_HARD)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group__parentnode=test_assignment)
        test_comment = baker.prepare('devilry_group.GroupComment',
                                     feedback_set=test_feedbackset,
                                     user_role=group_models.GroupComment.USER_ROLE_ADMIN)
        test_comment.clean()

    def test_clean_comment_student_assignment_period_expired(self):
        test_assignment = baker.make_recipe('devilry.apps.core.assignment_oldperiod_end')
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group__parentnode=test_assignment)
        test_comment = baker.prepare('devilry_group.GroupComment',
                                     feedback_set=test_feedbackset,
                                     user_role=group_models.GroupComment.USER_ROLE_STUDENT)
        with self.assertRaisesMessage(ValidationError, 'This assignment is on an inactive semester.'):
            test_comment.clean()

    def test_clean_comment_examienr_assignment_period_expired(self):
        test_assignment = baker.make_recipe('devilry.apps.core.assignment_oldperiod_end')
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group__parentnode=test_assignment)
        test_comment = baker.prepare('devilry_group.GroupComment',
                                     feedback_set=test_feedbackset,
                                     user_role=group_models.GroupComment.USER_ROLE_EXAMINER)
        with self.assertRaisesMessage(ValidationError, 'This assignment is on an inactive semester.'):
            test_comment.clean()

    def test_clean_comment_admin_assignment_period_expired(self):
        test_assignment = baker.make_recipe('devilry.apps.core.assignment_oldperiod_end')
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group__parentnode=test_assignment)
        test_comment = baker.prepare('devilry_group.GroupComment',
                                     feedback_set=test_feedbackset,
                                     user_role=group_models.GroupComment.USER_ROLE_ADMIN)
        with self.assertRaisesMessage(ValidationError, 'This assignment is on an inactive semester.'):
            test_comment.clean()


class TestGroupCommentQueryset(TestCase):
    def test_annotate_with_last_edited_history_has_attr(self):
        baker.make('devilry_group.GroupComment', text='test')
        groupcomment = group_models.GroupComment.objects.annotate_with_last_edit_history(
            requestuser_devilryrole='notstudent').get()
        self.assertTrue(hasattr(groupcomment, 'last_edithistory_datetime'))

    def test_annotate_with_last_edited_history_none(self):
        baker.make('devilry_group.GroupComment', text='test')
        groupcomment = group_models.GroupComment.objects.annotate_with_last_edit_history(
            requestuser_devilryrole='notstudent').get()
        self.assertIsNone(groupcomment.last_edithistory_datetime)

    def test_annotate_with_last_edited_history_private_devilryrole_student(self):
        test_groupcomment = baker.make('devilry_group.GroupComment', text='test')
        baker.make('devilry_group.GroupCommentEditHistory', group_comment=test_groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_PRIVATE)
        groupcomment = group_models.GroupComment.objects.annotate_with_last_edit_history(
            requestuser_devilryrole='student').get()
        self.assertIsNone(groupcomment.last_edithistory_datetime)

    def test_annotate_with_last_edited_history_examiners_and_admins_devilryrole_student(self):
        test_groupcomment = baker.make('devilry_group.GroupComment', text='test')
        baker.make('devilry_group.GroupCommentEditHistory', group_comment=test_groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)
        groupcomment = group_models.GroupComment.objects.annotate_with_last_edit_history(
            requestuser_devilryrole='student').get()
        self.assertIsNone(groupcomment.last_edithistory_datetime)

    def test_annotate_with_last_edited_history_everyone_devilryrole_student(self):
        test_groupcomment = baker.make('devilry_group.GroupComment', text='test')
        baker.make('devilry_group.GroupCommentEditHistory', group_comment=test_groupcomment,
                   visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        groupcomment = group_models.GroupComment.objects.annotate_with_last_edit_history(
            requestuser_devilryrole='student').get()
        self.assertIsNotNone(groupcomment.last_edithistory_datetime)

    def test_annotate_with_last_edited_history(self):
        test_groupcomment = baker.make('devilry_group.GroupComment', text='test')
        groupcommenthistory_last_edited = baker.make('devilry_group.GroupCommentEditHistory',
                                                     group_comment=test_groupcomment,
                                                     edited_datetime=timezone.now() - timezone.timedelta(days=1))
        groupcommenthistory_not_last_edited = baker.make('devilry_group.GroupCommentEditHistory',
                                                  group_comment=test_groupcomment,
                                                  edited_datetime=timezone.now() - timezone.timedelta(days=3))
        groupcomment = group_models.GroupComment.objects.annotate_with_last_edit_history(
            requestuser_devilryrole='notstudent').get()
        self.assertIsNotNone(groupcomment.last_edithistory_datetime)
        self.assertNotEqual(groupcomment.last_edithistory_datetime, groupcommenthistory_not_last_edited.edited_datetime)
        self.assertEqual(groupcomment.last_edithistory_datetime, groupcommenthistory_last_edited.edited_datetime)

    def test_annotate_with_last_edited_history_multiple_edits_sanity(self):
        test_groupcomment = baker.make('devilry_group.GroupComment', text='test')
        edited_datetime1 = baker.make('devilry_group.GroupCommentEditHistory',
                                      group_comment=test_groupcomment,
                                      edited_datetime=timezone.now() - timezone.timedelta(days=2)).edited_datetime
        edited_datetime2 = baker.make('devilry_group.GroupCommentEditHistory',
                                      group_comment=test_groupcomment,
                                      edited_datetime=timezone.now() - timezone.timedelta(minutes=2)).edited_datetime
        edited_datetime3 = baker.make('devilry_group.GroupCommentEditHistory',
                                      group_comment=test_groupcomment,
                                      edited_datetime=timezone.now() - timezone.timedelta(days=1)).edited_datetime
        groupcomment = group_models.GroupComment.objects.annotate_with_last_edit_history(
            requestuser_devilryrole='notstudent').get()
        self.assertNotEqual(groupcomment.last_edithistory_datetime, edited_datetime1)
        self.assertNotEqual(groupcomment.last_edithistory_datetime, edited_datetime3)
        self.assertEqual(groupcomment.last_edithistory_datetime, edited_datetime2)

    def test_annotations_not_duplicates_from_other_comments(self):
        comment_to_edited_datetime_map = {}
        for comment_counter in range(10):
            test_groupcomment = baker.make('devilry_group.GroupComment', text='test')
            edithistory = baker.make('devilry_group.GroupCommentEditHistory',
                                     group_comment=test_groupcomment,
                                     edited_datetime=timezone.now() - timezone.timedelta(days=comment_counter))
            comment_to_edited_datetime_map[test_groupcomment.id] = edithistory
        self.assertEqual(group_models.GroupComment.objects.count(), 10)
        self.assertEqual(group_models.GroupCommentEditHistory.objects.count(), 10)

        last_edited_datetime = None
        for group_comment in group_models.GroupComment.objects.annotate_with_last_edit_history(
                requestuser_devilryrole='notstudent'):
            if last_edited_datetime:
                self.assertNotEqual(group_comment.last_edithistory_datetime, last_edited_datetime)
            last_edited_datetime = group_comment.last_edithistory_datetime

    def test_annotate_with_last_edited_history_num_queries(self):
        for i in range(10):
            test_groupcomment = baker.make('devilry_group.GroupComment', text='test')
            baker.make('devilry_group.GroupCommentEditHistory', group_comment=test_groupcomment,
                       edited_datetime=timezone.now() - timezone.timedelta(days=2))
            baker.make('devilry_group.GroupCommentEditHistory', group_comment=test_groupcomment,
                       edited_datetime=timezone.now() - timezone.timedelta(minutes=2))
            baker.make('devilry_group.GroupCommentEditHistory', group_comment=test_groupcomment,
                       edited_datetime=timezone.now() - timezone.timedelta(days=1))
        self.assertEqual(group_models.GroupComment.objects.count(), 10)
        self.assertEqual(group_models.GroupCommentEditHistory.objects.count(), 30)
        with self.assertNumQueries(1):
            for group_comment in group_models.GroupComment.objects.annotate_with_last_edit_history(
                    requestuser_devilryrole='notstudent'):
                self.assertIsNotNone(group_comment.last_edithistory_datetime)
