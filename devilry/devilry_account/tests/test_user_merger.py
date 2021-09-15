from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_comment.models import Comment
from devilry.devilry_qualifiesforexam.models import QualifiesForFinalExam
from devilry.apps.core.models import Period, RelatedStudent, RelatedExaminer, Candidate, Examiner
from devilry.devilry_account.models import PermissionGroupUser
from devilry.devilry_account.user_merger import UserMerger
from django import test
from django.conf import settings
from unittest import mock
from model_bakery import baker


class TestUserMerger(test.TestCase):
    def test_merge_permission_group_user_objects(self):
        source_user = baker.make(settings.AUTH_USER_MODEL)
        target_user = baker.make(settings.AUTH_USER_MODEL)
        periodpermissiongroup = baker.make('devilry_account.PeriodPermissionGroup')
        baker.make('devilry_account.PermissionGroupUser',
                   user=source_user, permissiongroup=periodpermissiongroup.permissiongroup)
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup')
        baker.make('devilry_account.PermissionGroupUser',
                   user=source_user, permissiongroup=subjectpermissiongroup.permissiongroup)

        self.assertEqual(PermissionGroupUser.objects.filter(user=source_user).count(), 2)
        self.assertFalse(PermissionGroupUser.objects.filter(user=target_user).exists())
        UserMerger(
            source_user=source_user,
            target_user=target_user,
            pretend=False
        )._merge_permission_group_user_objects()
        self.assertFalse(PermissionGroupUser.objects.filter(user=source_user).exists())
        self.assertEqual(PermissionGroupUser.objects.filter(user=target_user).count(), 2)

    def test_merge_relatedstudent_objects(self):
        source_user = baker.make(settings.AUTH_USER_MODEL)
        target_user = baker.make(settings.AUTH_USER_MODEL)
        period1 = baker.make(Period)
        period2 = baker.make(Period)
        period3 = baker.make(Period)
        source_relatedstudent1 = baker.make(RelatedStudent, user=source_user, period=period1)
        source_relatedstudent2 = baker.make(RelatedStudent, user=source_user, period=period2)
        target_relatedstudent1 = baker.make(RelatedStudent, user=target_user, period=period2)
        target_relatedstudent2 = baker.make(RelatedStudent, user=target_user, period=period3)

        source_relatedstudent1_candidate1 = baker.make(
            Candidate, assignment_group__assignment__period=period1,
            relatedstudent=source_relatedstudent1)
        source_relatedstudent1_candidate2 = baker.make(
            Candidate, assignment_group__assignment__period=period1,
            relatedstudent=source_relatedstudent1)
        source_relatedstudent2_candidate1 = baker.make(
            Candidate, assignment_group__assignment__period=period2,
            relatedstudent=source_relatedstudent2)
        target_relatedstudent1_candidate1 = baker.make(
            Candidate, assignment_group__assignment__period=period2,
            relatedstudent=target_relatedstudent1)
        target_relatedstudent2_candidate1 = baker.make(
            Candidate, assignment_group__assignment__period=period3,
            relatedstudent=target_relatedstudent2)

        source_relatedstudent1_qualifies_for_final_exam = baker.make(
            QualifiesForFinalExam,
            relatedstudent=source_relatedstudent1)
        source_relatedstudent2_qualifies_for_final_exam = baker.make(
            QualifiesForFinalExam,
            relatedstudent=source_relatedstudent2)
        target_relatedstudent1_qualifies_for_final_exam = baker.make(
            QualifiesForFinalExam,
            relatedstudent=target_relatedstudent1)

        self.assertEqual(RelatedStudent.objects.filter(user=source_user).count(), 2)
        self.assertEqual(RelatedStudent.objects.filter(user=target_user).count(), 2)
        self.assertEqual(Candidate.objects.filter(relatedstudent__user=source_user).count(), 3)
        self.assertEqual(Candidate.objects.filter(relatedstudent__user=target_user).count(), 2)
        self.assertEqual(QualifiesForFinalExam.objects.filter(relatedstudent__user=source_user).count(), 2)
        self.assertEqual(QualifiesForFinalExam.objects.filter(relatedstudent__user=target_user).count(), 1)
        UserMerger(
            source_user=source_user,
            target_user=target_user,
            pretend=False
        )._merge_relatedstudent_objects()

        # Sanity checks
        self.assertEqual(RelatedStudent.objects.filter(user=source_user).count(), 0)
        self.assertEqual(RelatedStudent.objects.filter(user=target_user).count(), 3)
        self.assertEqual(Candidate.objects.filter(relatedstudent__user=source_user).count(), 0)
        self.assertEqual(Candidate.objects.filter(relatedstudent__user=target_user).count(), 5)
        self.assertEqual(QualifiesForFinalExam.objects.filter(relatedstudent__user=source_user).count(), 0)
        self.assertEqual(QualifiesForFinalExam.objects.filter(relatedstudent__user=target_user).count(), 3)

        # Detaled checks for RelatedStudent
        target_converted_from_source_relatedstudent1 = source_relatedstudent1
        target_converted_from_source_relatedstudent1.refresh_from_db()
        target_relatedstudent1.refresh_from_db()
        target_relatedstudent2.refresh_from_db()
        self.assertEqual(target_converted_from_source_relatedstudent1.user, target_user)
        self.assertFalse(RelatedStudent.objects.filter(id=source_relatedstudent2.id).exists())
        self.assertEqual(target_relatedstudent1.user, target_user)
        self.assertEqual(target_relatedstudent2.user, target_user)

        # Detailed checks for candidates
        self.assertEqual(Candidate.objects.filter(relatedstudent=target_converted_from_source_relatedstudent1).count(), 2)
        self.assertEqual(
            set(Candidate.objects.filter(relatedstudent=target_converted_from_source_relatedstudent1)),
            {source_relatedstudent1_candidate1, source_relatedstudent1_candidate2})

        self.assertEqual(Candidate.objects.filter(relatedstudent=source_relatedstudent2).count(), 0)

        self.assertEqual(Candidate.objects.filter(relatedstudent=target_relatedstudent1).count(), 2)
        self.assertEqual(
            set(Candidate.objects.filter(relatedstudent=target_relatedstudent1)),
            {source_relatedstudent2_candidate1, target_relatedstudent1_candidate1})

        self.assertEqual(Candidate.objects.filter(relatedstudent=target_relatedstudent2).count(), 1)
        self.assertEqual(
            Candidate.objects.filter(relatedstudent=target_relatedstudent2).first(),
            target_relatedstudent2_candidate1)

        # Detailed cheks for QualifiedForFinalExam
        self.assertEqual(QualifiesForFinalExam.objects.filter(relatedstudent=target_converted_from_source_relatedstudent1).count(), 1)
        self.assertEqual(
            QualifiesForFinalExam.objects.filter(relatedstudent=target_converted_from_source_relatedstudent1).first(),
            source_relatedstudent1_qualifies_for_final_exam)
        
        self.assertEqual(QualifiesForFinalExam.objects.filter(relatedstudent=source_relatedstudent2).count(), 0)

        self.assertEqual(QualifiesForFinalExam.objects.filter(relatedstudent=target_relatedstudent1).count(), 2)
        self.assertEqual(
            set(QualifiesForFinalExam.objects.filter(relatedstudent=target_relatedstudent1)),
            {source_relatedstudent2_qualifies_for_final_exam, target_relatedstudent1_qualifies_for_final_exam})

    def test_merge_relatedexaminer_objects(self):
        source_user = baker.make(settings.AUTH_USER_MODEL)
        target_user = baker.make(settings.AUTH_USER_MODEL)
        period1 = baker.make(Period)
        period2 = baker.make(Period)
        period3 = baker.make(Period)
        source_relatedexaminer1 = baker.make(RelatedExaminer, user=source_user, period=period1)
        source_relatedexaminer2 = baker.make(RelatedExaminer, user=source_user, period=period2)
        target_relatedexaminer1 = baker.make(RelatedExaminer, user=target_user, period=period2)
        target_relatedexaminer2 = baker.make(RelatedExaminer, user=target_user, period=period3)

        source_relatedexaminer1_examiner1 = baker.make(
            Examiner, assignmentgroup__assignment__period=period1,
            relatedexaminer=source_relatedexaminer1)
        source_relatedexaminer1_examiner2 = baker.make(
            Examiner, assignmentgroup__assignment__period=period1,
            relatedexaminer=source_relatedexaminer1)
        source_relatedexaminer2_examiner1 = baker.make(
            Examiner, assignmentgroup__assignment__period=period2,
            relatedexaminer=source_relatedexaminer2)
        target_relatedexaminer1_examiner1 = baker.make(
            Examiner, assignmentgroup__assignment__period=period2,
            relatedexaminer=target_relatedexaminer1)
        target_relatedexaminer2_examiner1 = baker.make(
            Examiner, assignmentgroup__assignment__period=period3,
            relatedexaminer=target_relatedexaminer2)

        self.assertEqual(RelatedExaminer.objects.filter(user=source_user).count(), 2)
        self.assertEqual(RelatedExaminer.objects.filter(user=target_user).count(), 2)
        self.assertEqual(Examiner.objects.filter(relatedexaminer__user=source_user).count(), 3)
        self.assertEqual(Examiner.objects.filter(relatedexaminer__user=target_user).count(), 2)
        UserMerger(
            source_user=source_user,
            target_user=target_user,
            pretend=False
        )._merge_relatedexaminer_objects()

        # Sanity checks
        self.assertEqual(RelatedExaminer.objects.filter(user=source_user).count(), 0)
        self.assertEqual(RelatedExaminer.objects.filter(user=target_user).count(), 3)
        self.assertEqual(Examiner.objects.filter(relatedexaminer__user=source_user).count(), 0)
        self.assertEqual(Examiner.objects.filter(relatedexaminer__user=target_user).count(), 5)

        # Detaled checks for RelatedExaminer
        target_converted_from_source_relatedexaminer1 = source_relatedexaminer1
        target_converted_from_source_relatedexaminer1.refresh_from_db()
        target_relatedexaminer1.refresh_from_db()
        target_relatedexaminer2.refresh_from_db()
        self.assertEqual(target_converted_from_source_relatedexaminer1.user, target_user)
        self.assertFalse(RelatedExaminer.objects.filter(id=source_relatedexaminer2.id).exists())
        self.assertEqual(target_relatedexaminer1.user, target_user)
        self.assertEqual(target_relatedexaminer2.user, target_user)

        # Detailed checks for examiners
        self.assertEqual(Examiner.objects.filter(relatedexaminer=target_converted_from_source_relatedexaminer1).count(), 2)
        self.assertEqual(
            set(Examiner.objects.filter(relatedexaminer=target_converted_from_source_relatedexaminer1)),
            {source_relatedexaminer1_examiner1, source_relatedexaminer1_examiner2})

        self.assertEqual(Examiner.objects.filter(relatedexaminer=source_relatedexaminer2).count(), 0)

        self.assertEqual(Examiner.objects.filter(relatedexaminer=target_relatedexaminer1).count(), 2)
        self.assertEqual(
            set(Examiner.objects.filter(relatedexaminer=target_relatedexaminer1)),
            {source_relatedexaminer2_examiner1, target_relatedexaminer1_examiner1})

        self.assertEqual(Examiner.objects.filter(relatedexaminer=target_relatedexaminer2).count(), 1)
        self.assertEqual(
            Examiner.objects.filter(relatedexaminer=target_relatedexaminer2).first(),
            target_relatedexaminer2_examiner1)

    def test_merge_comment_objects(self):
        source_user = baker.make(settings.AUTH_USER_MODEL)
        target_user = baker.make(settings.AUTH_USER_MODEL)
        comment1 = baker.make('devilry_comment.Comment', user=source_user)
        comment2 = baker.make('devilry_comment.Comment', user=source_user)
        comment3 = baker.make('devilry_comment.Comment', user=target_user)

        self.assertEqual(Comment.objects.filter(user=source_user).count(), 2)
        self.assertEqual(Comment.objects.filter(user=target_user).count(), 1)
        UserMerger(
            source_user=source_user,
            target_user=target_user,
            pretend=False
        )._merge_comment_objects()
        self.assertEqual(Comment.objects.filter(user=source_user).count(), 0)
        self.assertEqual(Comment.objects.filter(user=target_user).count(), 3)
        self.assertEqual(set(Comment.objects.filter(user=target_user)), {comment1, comment2, comment3})

    def test_merge_feedbackset_objects_created_by(self):
        source_user = baker.make(settings.AUTH_USER_MODEL)
        target_user = baker.make(settings.AUTH_USER_MODEL)
        feedbackset1 = baker.make('devilry_group.FeedbackSet', created_by=source_user)
        feedbackset2 = baker.make('devilry_group.FeedbackSet', created_by=source_user)
        feedbackset3 = baker.make('devilry_group.FeedbackSet', created_by=target_user)

        self.assertEqual(FeedbackSet.objects.filter(created_by=source_user).count(), 2)
        self.assertEqual(FeedbackSet.objects.filter(created_by=target_user).count(), 1)
        UserMerger(
            source_user=source_user,
            target_user=target_user,
            pretend=False
        )._merge_feedbackset_objects()
        self.assertEqual(FeedbackSet.objects.filter(created_by=source_user).count(), 0)
        self.assertEqual(FeedbackSet.objects.filter(created_by=target_user).count(), 3)
        self.assertEqual(set(FeedbackSet.objects.filter(created_by=target_user)), {feedbackset1, feedbackset2, feedbackset3})

    def test_merge_feedbackset_objects_last_updated_by(self):
        source_user = baker.make(settings.AUTH_USER_MODEL)
        target_user = baker.make(settings.AUTH_USER_MODEL)
        feedbackset1 = baker.make('devilry_group.FeedbackSet', last_updated_by=source_user)
        feedbackset2 = baker.make('devilry_group.FeedbackSet', last_updated_by=source_user)
        feedbackset3 = baker.make('devilry_group.FeedbackSet', last_updated_by=target_user)

        self.assertEqual(FeedbackSet.objects.filter(last_updated_by=source_user).count(), 2)
        self.assertEqual(FeedbackSet.objects.filter(last_updated_by=target_user).count(), 1)
        UserMerger(
            source_user=source_user,
            target_user=target_user,
            pretend=False
        )._merge_feedbackset_objects()
        self.assertEqual(FeedbackSet.objects.filter(last_updated_by=source_user).count(), 0)
        self.assertEqual(FeedbackSet.objects.filter(last_updated_by=target_user).count(), 3)
        self.assertEqual(set(FeedbackSet.objects.filter(last_updated_by=target_user)), {feedbackset1, feedbackset2, feedbackset3})

    def test_merge_feedbackset_objects_grading_published_by(self):
        source_user = baker.make(settings.AUTH_USER_MODEL)
        target_user = baker.make(settings.AUTH_USER_MODEL)
        feedbackset1 = baker.make('devilry_group.FeedbackSet', grading_published_by=source_user)
        feedbackset2 = baker.make('devilry_group.FeedbackSet', grading_published_by=source_user)
        feedbackset3 = baker.make('devilry_group.FeedbackSet', grading_published_by=target_user)

        self.assertEqual(FeedbackSet.objects.filter(grading_published_by=source_user).count(), 2)
        self.assertEqual(FeedbackSet.objects.filter(grading_published_by=target_user).count(), 1)
        UserMerger(
            source_user=source_user,
            target_user=target_user,
            pretend=False
        )._merge_feedbackset_objects()
        self.assertEqual(FeedbackSet.objects.filter(grading_published_by=source_user).count(), 0)
        self.assertEqual(FeedbackSet.objects.filter(grading_published_by=target_user).count(), 3)
        self.assertEqual(set(FeedbackSet.objects.filter(grading_published_by=target_user)), {feedbackset1, feedbackset2, feedbackset3})

    def test_merge_sanity(self):
        source_user = baker.make(settings.AUTH_USER_MODEL)
        target_user = baker.make(settings.AUTH_USER_MODEL)
        merger = UserMerger(
            source_user=source_user,
            target_user=target_user,
            pretend=False
        )
        merger._merge_permission_group_user_objects = mock.MagicMock()
        merger._merge_relatedstudent_objects = mock.MagicMock()
        merger._merge_relatedexaminer_objects = mock.MagicMock()
        merger._merge_comment_objects = mock.MagicMock()
        merger._merge_feedbackset_objects = mock.MagicMock()
        merger.merge()
        merger._merge_permission_group_user_objects.assert_called_once()
        merger._merge_relatedstudent_objects.assert_called_once()
        merger._merge_relatedexaminer_objects.assert_called_once()
        merger._merge_comment_objects.assert_called_once()
        merger._merge_feedbackset_objects.assert_called_once()
