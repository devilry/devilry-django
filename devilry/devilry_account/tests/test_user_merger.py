from devilry.devilry_qualifiesforexam.models import QualifiesForFinalExam
from devilry.apps.core.models import Period, RelatedStudent, RelatedExaminer, Candidate, Examiner
from devilry.devilry_account.models import PermissionGroupUser
from devilry.devilry_account.user_merger import UserMerger
from django import test
from django.conf import settings
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
