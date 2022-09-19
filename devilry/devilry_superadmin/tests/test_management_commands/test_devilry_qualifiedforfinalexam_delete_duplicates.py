from django.core.management import call_command
import mock
from devilry.devilry_qualifiesforexam.models import QualifiesForFinalExam
from devilry.apps.core.models import Subject, Period, RelatedStudent
from django import test
from django.conf import settings
from model_bakery import baker


class TestQualifiedForFinalExamMerge(test.TestCase):
    def test_merge_relatedstudent_objects(self):
        user_a = baker.make(settings.AUTH_USER_MODEL, shortname='user_a')
        user_b = baker.make(settings.AUTH_USER_MODEL, shortname='user_b')
        subject1 = baker.make(Subject, short_name='subject1')
        period1 = baker.make(Period, short_name='period1', parentnode=subject1)
        period2 = baker.make(Period, short_name='period2', parentnode=subject1)
        period3 = baker.make(Period, short_name='period3', parentnode=subject1)
        period4 = baker.make(Period, short_name='period4', parentnode=subject1)
        relatedstudent_a_1 = baker.make(RelatedStudent, user=user_a, period=period1)
        relatedstudent_a_2 = baker.make(RelatedStudent, user=user_a, period=period2)
        relatedstudent_a_3 = baker.make(RelatedStudent, user=user_a, period=period3)
        relatedstudent_b_2 = baker.make(RelatedStudent, user=user_b, period=period2)
        relatedstudent_b_3 = baker.make(RelatedStudent, user=user_b, period=period3)
        relatedstudent_b_4 = baker.make(RelatedStudent, user=user_b, period=period4)

        qualifiesforfinalexam_a_1 = baker.make(QualifiesForFinalExam, relatedstudent=relatedstudent_a_1)
        qualifiesforfinalexam_a_2 = baker.make(QualifiesForFinalExam, relatedstudent=relatedstudent_a_2)
        qualifiesforfinalexam_a_3 = baker.make(QualifiesForFinalExam, relatedstudent=relatedstudent_a_3)
        qualifiesforfinalexam_b_2 = baker.make(QualifiesForFinalExam, relatedstudent=relatedstudent_b_2)
        qualifiesforfinalexam_b_3 = baker.make(QualifiesForFinalExam, relatedstudent=relatedstudent_b_3)
        qualifiesforfinalexam_b_4 = baker.make(QualifiesForFinalExam, relatedstudent=relatedstudent_b_4)

        self.assertEqual(QualifiesForFinalExam.objects.filter(relatedstudent__user=user_a).count(), 3)
        self.assertEqual(QualifiesForFinalExam.objects.filter(relatedstudent__user=user_b).count(), 3)

        delete_users = [user_a, user_b]
        def select_username_to_delete_mock(user_a, user_b, period):
            return delete_users.pop(0)

        with mock.patch('devilry.devilry_superadmin.management.commands.devilry_qualifiedforfinalexam_delete_duplicates.select_username_to_delete', select_username_to_delete_mock):
            call_command('devilry_qualifiedforfinalexam_delete_duplicates', '--user-a', 'user_a', '--user-b', 'user_b')

        self.assertEqual(QualifiesForFinalExam.objects.filter(relatedstudent__user=user_a).count(), 2)
        self.assertEqual(QualifiesForFinalExam.objects.filter(relatedstudent__user=user_b).count(), 2)

        self.assertTrue(QualifiesForFinalExam.objects.filter(id=qualifiesforfinalexam_a_1.id).exists())
        self.assertFalse(QualifiesForFinalExam.objects.filter(id=qualifiesforfinalexam_a_2.id).exists())
        self.assertTrue(QualifiesForFinalExam.objects.filter(id=qualifiesforfinalexam_a_3.id).exists())
        
        self.assertTrue(QualifiesForFinalExam.objects.filter(id=qualifiesforfinalexam_b_2.id).exists())
        self.assertFalse(QualifiesForFinalExam.objects.filter(id=qualifiesforfinalexam_b_3.id).exists())
        self.assertTrue(QualifiesForFinalExam.objects.filter(id=qualifiesforfinalexam_b_4.id).exists())