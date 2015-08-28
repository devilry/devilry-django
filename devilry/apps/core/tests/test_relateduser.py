from django.db import IntegrityError

from django.test import TestCase
from model_mommy import mommy
from devilry.apps.core.models import RelatedExaminer
from devilry.devilry_account.exceptions import IllegalOperationError

from devilry.project.develop.testhelpers.corebuilder import UserBuilder2


class TestRelatedStudentModel(TestCase):
    def test_unique_in_period(self):
        testperiod = mommy.make('core.Period')
        testuser = UserBuilder2().user
        mommy.make('core.RelatedStudent', period=testperiod, user=testuser)
        with self.assertRaises(IntegrityError):
            mommy.make('core.RelatedStudent', period=testperiod, user=testuser)


class TestRelatedExaminerModel(TestCase):
    def test_unique_in_period(self):
        testperiod = mommy.make('core.Period')
        testuser = UserBuilder2().user
        mommy.make('core.RelatedExaminer', period=testperiod, user=testuser)
        with self.assertRaises(IntegrityError):
            mommy.make('core.RelatedExaminer', period=testperiod, user=testuser)


class TestRelatedExaminerManager(TestCase):
    def test_bulk_create_from_emails_not_allowed_with_username_auth_backend(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            with self.assertRaises(IllegalOperationError):
                RelatedExaminer.objects.bulk_create_from_emails(testperiod, [])

    def test_bulk_create_from_emails_empty_input_list(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            result = RelatedExaminer.objects.bulk_create_from_emails(testperiod, [])
            self.assertEqual(0, result.created_relatedusers_queryset.count())
            self.assertEqual(0, RelatedExaminer.objects.count())
            self.assertEqual(set(), result.existing_relateduser_emails_set)

    def test_bulk_create_from_emails_single_new(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            result = RelatedExaminer.objects.bulk_create_from_emails(
                testperiod, ['testuser@example.com'])

            self.assertEqual(1, result.created_relatedusers_queryset.count())
            self.assertEqual(1, RelatedExaminer.objects.count())
            self.assertEqual('testuser@example.com',
                             RelatedExaminer.objects.first().user.shortname)
            self.assertEqual(set(), result.existing_relateduser_emails_set)

    def test_bulk_create_from_emails_multiple_new(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            result = RelatedExaminer.objects.bulk_create_from_emails(
                testperiod, ['testuser1@example.com', 'testuser2@example.com', 'testuser3@example.com'])

            self.assertEqual(3, result.created_relatedusers_queryset.count())
            self.assertEqual(3, RelatedExaminer.objects.count())
            self.assertEqual({'testuser1@example.com', 'testuser2@example.com', 'testuser3@example.com'},
                             {relatedexaminer.user.shortname for relatedexaminer in RelatedExaminer.objects.all()})
            self.assertEqual(set(), result.existing_relateduser_emails_set)

    def test_bulk_create_from_emails_exclude_existing(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer',
                   period=testperiod,
                   user=UserBuilder2().add_emails('testuser1@example.com').user)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):

            result = RelatedExaminer.objects.bulk_create_from_emails(
                period=testperiod,
                emails=['testuser1@example.com', 'testuser2@example.com'])

            self.assertEqual(2, RelatedExaminer.objects.count())
            self.assertEqual(1, result.created_relatedusers_queryset.count())
            self.assertEqual('testuser2@example.com',
                             result.created_relatedusers_queryset.first().user.shortname)
            self.assertEqual({'testuser1@example.com'},
                             result.existing_relateduser_emails_set)

    def test_bulk_create_from_emails_exclude_existing_in_other_period(self):
        testperiod = mommy.make('core.Period')
        otherperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer',
                   period=otherperiod,
                   user=UserBuilder2(shortname='testuser1@example.com').add_emails('testuser1@example.com').user)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            result = RelatedExaminer.objects.bulk_create_from_emails(
                period=testperiod,
                emails=['testuser1@example.com', 'testuser2@example.com'])

            self.assertEqual(3, RelatedExaminer.objects.count())
            self.assertEqual(2, result.created_relatedusers_queryset.count())
            self.assertEqual({'testuser1@example.com', 'testuser2@example.com'},
                             {relatedexaminer.user.shortname
                              for relatedexaminer in result.created_relatedusers_queryset.all()})
            self.assertEqual(set(), result.existing_relateduser_emails_set)


class TestRelatedStudentSyncSystemTag(TestCase):
    def test_tag_unique_for_relatedstudent(self):
        testrelatedstudent = mommy.make('core.RelatedStudent')
        mommy.make('core.RelatedStudentSyncSystemTag', tag='testtag',
                   relatedstudent=testrelatedstudent)
        with self.assertRaises(IntegrityError):
            mommy.make('core.RelatedStudentSyncSystemTag', tag='testtag',
                       relatedstudent=testrelatedstudent)


class TestRelatedExaminerSyncSystemTag(TestCase):
    def test_tag_unique_for_relatedexaminer(self):
        testrelatedexaminer = mommy.make('core.RelatedExaminer')
        mommy.make('core.RelatedExaminerSyncSystemTag', tag='testtag',
                   relatedexaminer=testrelatedexaminer)
        with self.assertRaises(IntegrityError):
            mommy.make('core.RelatedExaminerSyncSystemTag', tag='testtag',
                       relatedexaminer=testrelatedexaminer)
