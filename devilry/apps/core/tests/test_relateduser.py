from django.db import IntegrityError
from django.test import TestCase
from model_mommy import mommy

from devilry.apps.core.models import RelatedExaminer, RelatedStudent
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

    def test_bulk_create_from_usernames_not_allowed_with_username_auth_backend(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            with self.assertRaises(IllegalOperationError):
                RelatedExaminer.objects.bulk_create_from_usernames(testperiod, [])

    def test_bulk_create_from_usernames_empty_input_list(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            result = RelatedExaminer.objects.bulk_create_from_usernames(testperiod, [])
            self.assertEqual(0, result.created_relatedusers_queryset.count())
            self.assertEqual(0, RelatedExaminer.objects.count())
            self.assertEqual(set(), result.existing_relateduser_usernames_set)

    def test_bulk_create_from_usernames_single_new(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            result = RelatedExaminer.objects.bulk_create_from_usernames(
                testperiod, ['testuser'])

            self.assertEqual(1, result.created_relatedusers_queryset.count())
            self.assertEqual(1, RelatedExaminer.objects.count())
            self.assertEqual('testuser',
                             RelatedExaminer.objects.first().user.shortname)
            self.assertEqual(set(), result.existing_relateduser_usernames_set)

    def test_bulk_create_from_usernames_multiple_new(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            result = RelatedExaminer.objects.bulk_create_from_usernames(
                testperiod, ['testuser1', 'testuser2', 'testuser3'])

            self.assertEqual(3, result.created_relatedusers_queryset.count())
            self.assertEqual(3, RelatedExaminer.objects.count())
            self.assertEqual({'testuser1', 'testuser2', 'testuser3'},
                             {relatedexaminer.user.shortname for relatedexaminer in RelatedExaminer.objects.all()})
            self.assertEqual(set(), result.existing_relateduser_usernames_set)

    def test_bulk_create_from_usernames_exclude_existing(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer',
                   period=testperiod,
                   user=UserBuilder2().add_usernames('testuser1').user)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            result = RelatedExaminer.objects.bulk_create_from_usernames(
                period=testperiod,
                usernames=['testuser1', 'testuser2'])

            self.assertEqual(2, RelatedExaminer.objects.count())
            self.assertEqual(1, result.created_relatedusers_queryset.count())
            self.assertEqual('testuser2',
                             result.created_relatedusers_queryset.first().user.shortname)
            self.assertEqual({'testuser1'},
                             result.existing_relateduser_usernames_set)

    def test_bulk_create_from_usernames_exclude_existing_in_other_period(self):
        testperiod = mommy.make('core.Period')
        otherperiod = mommy.make('core.Period')
        mommy.make('core.RelatedExaminer',
                   period=otherperiod,
                   user=UserBuilder2(shortname='testuser1').add_usernames('testuser1').user)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            result = RelatedExaminer.objects.bulk_create_from_usernames(
                period=testperiod,
                usernames=['testuser1', 'testuser2'])

            self.assertEqual(3, RelatedExaminer.objects.count())
            self.assertEqual(2, result.created_relatedusers_queryset.count())
            self.assertEqual({'testuser1', 'testuser2'},
                             {relatedexaminer.user.shortname
                              for relatedexaminer in result.created_relatedusers_queryset.all()})
            self.assertEqual(set(), result.existing_relateduser_usernames_set)


class TestRelatedStudentManager(TestCase):
    def test_bulk_create_from_emails_not_allowed_with_username_auth_backend(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            with self.assertRaises(IllegalOperationError):
                RelatedStudent.objects.bulk_create_from_emails(testperiod, [])

    def test_bulk_create_from_emails_empty_input_list(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            result = RelatedStudent.objects.bulk_create_from_emails(testperiod, [])
            self.assertEqual(0, result.created_relatedusers_queryset.count())
            self.assertEqual(0, RelatedStudent.objects.count())
            self.assertEqual(set(), result.existing_relateduser_emails_set)

    def test_bulk_create_from_emails_single_new(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            result = RelatedStudent.objects.bulk_create_from_emails(
                testperiod, ['testuser@example.com'])

            self.assertEqual(1, result.created_relatedusers_queryset.count())
            self.assertEqual(1, RelatedStudent.objects.count())
            self.assertEqual('testuser@example.com',
                             RelatedStudent.objects.first().user.shortname)
            self.assertEqual(set(), result.existing_relateduser_emails_set)

    def test_bulk_create_from_emails_multiple_new(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            result = RelatedStudent.objects.bulk_create_from_emails(
                testperiod, ['testuser1@example.com', 'testuser2@example.com', 'testuser3@example.com'])

            self.assertEqual(3, result.created_relatedusers_queryset.count())
            self.assertEqual(3, RelatedStudent.objects.count())
            self.assertEqual({'testuser1@example.com', 'testuser2@example.com', 'testuser3@example.com'},
                             {relatedexaminer.user.shortname for relatedexaminer in RelatedStudent.objects.all()})
            self.assertEqual(set(), result.existing_relateduser_emails_set)

    def test_bulk_create_from_emails_exclude_existing(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent',
                   period=testperiod,
                   user=UserBuilder2().add_emails('testuser1@example.com').user)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            result = RelatedStudent.objects.bulk_create_from_emails(
                period=testperiod,
                emails=['testuser1@example.com', 'testuser2@example.com'])

            self.assertEqual(2, RelatedStudent.objects.count())
            self.assertEqual(1, result.created_relatedusers_queryset.count())
            self.assertEqual('testuser2@example.com',
                             result.created_relatedusers_queryset.first().user.shortname)
            self.assertEqual({'testuser1@example.com'},
                             result.existing_relateduser_emails_set)

    def test_bulk_create_from_emails_exclude_existing_in_other_period(self):
        testperiod = mommy.make('core.Period')
        otherperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent',
                   period=otherperiod,
                   user=UserBuilder2(shortname='testuser1@example.com').add_emails('testuser1@example.com').user)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            result = RelatedStudent.objects.bulk_create_from_emails(
                period=testperiod,
                emails=['testuser1@example.com', 'testuser2@example.com'])

            self.assertEqual(3, RelatedStudent.objects.count())
            self.assertEqual(2, result.created_relatedusers_queryset.count())
            self.assertEqual({'testuser1@example.com', 'testuser2@example.com'},
                             {relatedexaminer.user.shortname
                              for relatedexaminer in result.created_relatedusers_queryset.all()})
            self.assertEqual(set(), result.existing_relateduser_emails_set)

    def test_bulk_create_from_usernames_not_allowed_with_username_auth_backend(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            with self.assertRaises(IllegalOperationError):
                RelatedStudent.objects.bulk_create_from_usernames(testperiod, [])

    def test_bulk_create_from_usernames_empty_input_list(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            result = RelatedStudent.objects.bulk_create_from_usernames(testperiod, [])
            self.assertEqual(0, result.created_relatedusers_queryset.count())
            self.assertEqual(0, RelatedStudent.objects.count())
            self.assertEqual(set(), result.existing_relateduser_usernames_set)

    def test_bulk_create_from_usernames_single_new(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            result = RelatedStudent.objects.bulk_create_from_usernames(
                testperiod, ['testuser'])

            self.assertEqual(1, result.created_relatedusers_queryset.count())
            self.assertEqual(1, RelatedStudent.objects.count())
            self.assertEqual('testuser',
                             RelatedStudent.objects.first().user.shortname)
            self.assertEqual(set(), result.existing_relateduser_usernames_set)

    def test_bulk_create_from_usernames_multiple_new(self):
        testperiod = mommy.make('core.Period')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            result = RelatedStudent.objects.bulk_create_from_usernames(
                testperiod, ['testuser1', 'testuser2', 'testuser3'])

            self.assertEqual(3, result.created_relatedusers_queryset.count())
            self.assertEqual(3, RelatedStudent.objects.count())
            self.assertEqual({'testuser1', 'testuser2', 'testuser3'},
                             {relatedexaminer.user.shortname for relatedexaminer in RelatedStudent.objects.all()})
            self.assertEqual(set(), result.existing_relateduser_usernames_set)

    def test_bulk_create_from_usernames_exclude_existing(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent',
                   period=testperiod,
                   user=UserBuilder2().add_usernames('testuser1').user)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            result = RelatedStudent.objects.bulk_create_from_usernames(
                period=testperiod,
                usernames=['testuser1', 'testuser2'])

            self.assertEqual(2, RelatedStudent.objects.count())
            self.assertEqual(1, result.created_relatedusers_queryset.count())
            self.assertEqual('testuser2',
                             result.created_relatedusers_queryset.first().user.shortname)
            self.assertEqual({'testuser1'},
                             result.existing_relateduser_usernames_set)

    def test_bulk_create_from_usernames_exclude_existing_in_other_period(self):
        testperiod = mommy.make('core.Period')
        otherperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent',
                   period=otherperiod,
                   user=UserBuilder2(shortname='testuser1').add_usernames('testuser1').user)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            result = RelatedStudent.objects.bulk_create_from_usernames(
                period=testperiod,
                usernames=['testuser1', 'testuser2'])

            self.assertEqual(3, RelatedStudent.objects.count())
            self.assertEqual(2, result.created_relatedusers_queryset.count())
            self.assertEqual({'testuser1', 'testuser2'},
                             {relatedexaminer.user.shortname
                              for relatedexaminer in result.created_relatedusers_queryset.all()})
            self.assertEqual(set(), result.existing_relateduser_usernames_set)


class TestRelatedStudentQueryset(TestCase):
    def test_get_userid_to_candidateid_map_no_relatedstudents(self):
        testperiod = mommy.make('core.Period')
        self.assertEqual(dict(),
                         testperiod.relatedstudent_set.get_userid_to_candidateid_map())

    def test_get_userid_to_candidateid_map_ignore_candidate_id_none(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent',
                   period=testperiod,
                   candidate_id=None)
        self.assertEqual(dict(),
                         testperiod.relatedstudent_set.get_userid_to_candidateid_map())

    def test_get_userid_to_candidateid_map_ignore_candidate_id_emptystring(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent',
                   period=testperiod,
                   candidate_id='')
        self.assertEqual(dict(),
                         testperiod.relatedstudent_set.get_userid_to_candidateid_map())

    def test_get_userid_to_candidateid_map(self):
        testperiod = mommy.make('core.Period')
        relatedstudent1 = mommy.make('core.RelatedStudent',
                                     period=testperiod,
                                     candidate_id='a')
        relatedstudent2 = mommy.make('core.RelatedStudent',
                                     period=testperiod,
                                     candidate_id='b')
        relatedstudent3 = mommy.make('core.RelatedStudent',
                                     period=testperiod,
                                     candidate_id='c')
        self.assertEqual(
            {
                relatedstudent1.user_id: 'a',
                relatedstudent2.user_id: 'b',
                relatedstudent3.user_id: 'c',
            },
            testperiod.relatedstudent_set.get_userid_to_candidateid_map())


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
