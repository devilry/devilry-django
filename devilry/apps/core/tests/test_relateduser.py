from django.conf import settings
from django.db import IntegrityError
from django.test import TestCase
from model_mommy import mommy

from devilry.apps.core.models import RelatedExaminer, RelatedStudent
from devilry.devilry_account.exceptions import IllegalOperationError
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.project.develop.testhelpers.corebuilder import UserBuilder2


class TestRelatedStudentModel(TestCase):
    def test_unique_in_period(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.RelatedStudent', period=testperiod, user=testuser)
        with self.assertRaises(IntegrityError):
            mommy.make('core.RelatedStudent', period=testperiod, user=testuser)

    def test_get_anonymous_name_missing_both_anonymous_id_and_candidate_id(self):
        relatedstudent = mommy.make('core.RelatedStudent')
        self.assertEqual('Automatic anonymous ID missing', relatedstudent.get_anonymous_name())

    def test_get_anonymous_name_has_anonymous_id_but_not_candidate_id(self):
        relatedstudent = mommy.make('core.RelatedStudent',
                                    automatic_anonymous_id='MyAutomaticID')
        self.assertEqual('MyAutomaticID', relatedstudent.get_anonymous_name())

    def test_get_anonymous_name_has_anonymous_id_and_candidate_id(self):
        relatedstudent = mommy.make('core.RelatedStudent',
                                    automatic_anonymous_id='MyAutomaticID',
                                    candidate_id='MyCandidateID')
        self.assertEqual('MyCandidateID', relatedstudent.get_anonymous_name())

    def test_get_anonymous_name_no_anonymous_id_but_has_candidate_id(self):
        relatedstudent = mommy.make('core.RelatedStudent',
                                    candidate_id='MyCandidateID')
        self.assertEqual('MyCandidateID', relatedstudent.get_anonymous_name())


class TestRelatedExaminerModel(TestCase):
    def test_unique_in_period(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.RelatedExaminer', period=testperiod, user=testuser)
        with self.assertRaises(IntegrityError):
            mommy.make('core.RelatedExaminer', period=testperiod, user=testuser)

    def test_get_anonymous_name_missing_anonymous_id(self):
        relatedexaminer = mommy.make('core.RelatedExaminer')
        self.assertEqual('Automatic anonymous ID missing', relatedexaminer.get_anonymous_name())

    def test_get_anonymous_name_has_anonymous_id(self):
        relatedexaminer = mommy.make('core.RelatedExaminer',
                                    automatic_anonymous_id='MyAutomaticID')
        self.assertEqual('MyAutomaticID', relatedexaminer.get_anonymous_name())


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


class TestRelatedStudentQuerySet(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __make_published_feedbackset_for_relatedstudent(self, relatedstudent, assignment, grading_points=0):
        from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_first_attempt_published(group=group, grading_points=grading_points)
        mommy.make('core.Candidate', assignment_group=group, relatedstudent=relatedstudent)
        return relatedstudent

    def test_annotate_with_total_grading_points_assignments_filter_sanity_before_annotation(self):
        test_assignment1 = mommy.make('core.Assignment', max_points=50)
        test_assignment2 = mommy.make('core.Assignment', max_points=50)
        relatedstudent = mommy.make('core.RelatedStudent')
        queryset = RelatedStudent.objects \
            .filter(candidate__assignment_group__parentnode_id__in=[test_assignment1.id, test_assignment2.id])\
            .annotate_with_total_grading_points(assignment_ids=[test_assignment1.id, test_assignment2.id])
        self.assertNotIn(relatedstudent, queryset)

    def test_annotate_with_total_grading_points_sanity(self):
        test_assignment1 = mommy.make('core.Assignment', max_points=50)
        test_assignment2 = mommy.make('core.Assignment', max_points=50)
        relatedstudent = mommy.make('core.RelatedStudent')
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent,
            assignment=test_assignment1,
            grading_points=25)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent,
            assignment=test_assignment2,
            grading_points=25)
        queryset = RelatedStudent.objects \
            .annotate_with_total_grading_points(assignment_ids=[test_assignment1.id, test_assignment2.id])
        self.assertEqual(queryset.get(id=relatedstudent.id).grade_points_total, 50)

    def test_annotated_with_total_grading_points_zero_for_relatedstudent_not_on_assignment(self):
        test_assignment1 = mommy.make('core.Assignment', max_points=50)
        test_assignment2 = mommy.make('core.Assignment', max_points=50)
        relatedstudent = mommy.make('core.RelatedStudent')
        queryset = RelatedStudent.objects \
            .annotate_with_total_grading_points(assignment_ids=[test_assignment1.id, test_assignment2.id])
        self.assertEqual(queryset.get(id=relatedstudent.id).grade_points_total, 0)

    def test_annotate_with_total_points_relatedstudent_not_on_one_assignment(self):
        test_assignment1 = mommy.make('core.Assignment', max_points=50)
        test_assignment2 = mommy.make('core.Assignment', max_points=50)
        relatedstudent = mommy.make('core.RelatedStudent')
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent,
            assignment=test_assignment1,
            grading_points=25)
        queryset = RelatedStudent.objects \
            .annotate_with_total_grading_points(assignment_ids=[test_assignment1.id, test_assignment2.id])
        self.assertEqual(queryset.get(id=relatedstudent.id).grade_points_total, 25)

    def test_annotate_with_total_points_relatedstudent_not_on_any_assignment(self):
        test_assignment1 = mommy.make('core.Assignment', max_points=50)
        test_assignment2 = mommy.make('core.Assignment', max_points=50)
        relatedstudent = mommy.make('core.RelatedStudent')
        queryset = RelatedStudent.objects \
            .annotate_with_total_grading_points(assignment_ids=[test_assignment1.id, test_assignment2.id])
        self.assertEqual(queryset.get(id=relatedstudent.id).grade_points_total, 0)

    def test_annotate_with_total_grading_points_multiple_relatedstudents(self):
        test_assignment1 = mommy.make('core.Assignment', max_points=50)
        test_assignment2 = mommy.make('core.Assignment', max_points=50)
        relatedstudent1 = mommy.make('core.RelatedStudent', user__fullname='Test1')
        relatedstudent2 = mommy.make('core.RelatedStudent', user__fullname='Test2')
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent1,
            assignment=test_assignment1,
            grading_points=25)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent1,
            assignment=test_assignment2,
            grading_points=25)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent2,
            assignment=test_assignment1,
            grading_points=10)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent2,
            assignment=test_assignment2,
            grading_points=10)
        queryset = RelatedStudent.objects \
            .annotate_with_total_grading_points(assignment_ids=[test_assignment1.id, test_assignment2.id])
        self.assertEqual(queryset.get(id=relatedstudent1.id).grade_points_total, 50)
        self.assertEqual(queryset.get(id=relatedstudent2.id).grade_points_total, 20)

    def test_annotate_with_total_points_query_count(self):
        test_assignment1 = mommy.make('core.Assignment', max_points=50)
        test_assignment2 = mommy.make('core.Assignment', max_points=50)
        relatedstudent1 = mommy.make('core.RelatedStudent', user__fullname='Test1')
        relatedstudent2 = mommy.make('core.RelatedStudent', user__fullname='Test2')
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent1,
            assignment=test_assignment1,
            grading_points=25)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent1,
            assignment=test_assignment2,
            grading_points=25)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent2,
            assignment=test_assignment1,
            grading_points=10)
        self.__make_published_feedbackset_for_relatedstudent(
            relatedstudent=relatedstudent2,
            assignment=test_assignment2,
            grading_points=10)
        with self.assertNumQueries(1):
            queryset = RelatedStudent.objects \
                .annotate_with_total_grading_points(assignment_ids=[test_assignment1.id, test_assignment2.id])
            len(queryset)

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


class TestRelatedStudentQuerySetPrefetchSyncsystemtags(TestCase):
    def test_none(self):
        relatedstudent = mommy.make('core.RelatedStudent')
        prefetched_relatedstudent = RelatedStudent.objects.prefetch_syncsystemtag_objects()\
            .get(id=relatedstudent.id)
        self.assertEqual([], prefetched_relatedstudent.syncsystemtag_objects)

    def test_ordering(self):
        testperiod = mommy.make('core.Period')
        relatedstudent = mommy.make('core.RelatedStudent', period=testperiod)
        testperiodtag_a = mommy.make('core.PeriodTag', period=testperiod, tag='a')
        testperiodtag_b = mommy.make('core.PeriodTag', period=testperiod, tag='b')
        testperiodtag_c = mommy.make('core.PeriodTag', period=testperiod, tag='c')

        testperiodtag_b.relatedstudents.add(relatedstudent)
        testperiodtag_a.relatedstudents.add(relatedstudent)
        testperiodtag_c.relatedstudents.add(relatedstudent)
        prefetched_relatedstudent = RelatedStudent.objects.prefetch_syncsystemtag_objects()\
            .get(id=relatedstudent.id)
        self.assertEqual([testperiodtag_a, testperiodtag_b, testperiodtag_c],
                         prefetched_relatedstudent.syncsystemtag_objects)

    def test_syncsystemtag_stringlist_not_using_prefetch_syncsystemtag_objects(self):
        relatedstudent = mommy.make('core.RelatedStudent')
        with self.assertRaisesMessage(AttributeError,
                                      'The syncsystemtag_stringlist property requires '
                                      'RelatedStudentQuerySet.prefetch_syncsystemtag_objects().'):
            str(relatedstudent.syncsystemtag_stringlist)

    def test_syncsystemtag_stringlist(self):
        testperiod = mommy.make('core.Period')
        relatedstudent = mommy.make('core.RelatedStudent', period=testperiod)
        testperiodtag_a = mommy.make('core.PeriodTag', period=testperiod, tag='a')
        testperiodtag_b = mommy.make('core.PeriodTag', period=testperiod, tag='b')
        testperiodtag_b.relatedstudents.add(relatedstudent)
        testperiodtag_a.relatedstudents.add(relatedstudent)
        prefetched_relatedstudent = RelatedStudent.objects.prefetch_syncsystemtag_objects()\
            .get(id=relatedstudent.id)
        self.assertEqual(['a', 'b'], prefetched_relatedstudent.syncsystemtag_stringlist)


class RelatedExaminerQuerySetAnnotateWithNumberOfGroupsOnAssignment(TestCase):
    def test_no_groups(self):
        relatedexaminer = mommy.make('core.RelatedExaminer')
        testassignment = mommy.make('core.Assignment')
        queryset = RelatedExaminer.objects\
            .annotate_with_number_of_groups_on_assignment(assignment=testassignment)
        annotated_relatedexaminer = queryset.get(id=relatedexaminer.id)
        self.assertEqual(
            0, annotated_relatedexaminer.number_of_groups_on_assignment)

    def test_not_within_assignment(self):
        relatedexaminer = mommy.make('core.RelatedExaminer')
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.Examiner', relatedexaminer=relatedexaminer)  # Not within testassignment
        queryset = RelatedExaminer.objects\
            .annotate_with_number_of_groups_on_assignment(assignment=testassignment)
        annotated_relatedexaminer = queryset.get(id=relatedexaminer.id)
        self.assertEqual(
            0, annotated_relatedexaminer.number_of_groups_on_assignment)

    def test_multiple_groups(self):
        relatedexaminer = mommy.make('core.RelatedExaminer')
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.Examiner',
                   assignmentgroup__parentnode=testassignment,
                   relatedexaminer=relatedexaminer)
        mommy.make('core.Examiner',
                   assignmentgroup__parentnode=testassignment,
                   relatedexaminer=relatedexaminer)
        queryset = RelatedExaminer.objects\
            .annotate_with_number_of_groups_on_assignment(assignment=testassignment)
        annotated_relatedexaminer = queryset.get(id=relatedexaminer.id)
        self.assertEqual(
            2, annotated_relatedexaminer.number_of_groups_on_assignment)

    def test_multiple_relatedexaminers(self):
        relatedexaminer1 = mommy.make('core.RelatedExaminer')
        relatedexaminer2 = mommy.make('core.RelatedExaminer')
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.Examiner',
                   assignmentgroup__parentnode=testassignment,
                   relatedexaminer=relatedexaminer1)
        mommy.make('core.Examiner',
                   assignmentgroup__parentnode=testassignment,
                   relatedexaminer=relatedexaminer1)
        mommy.make('core.Examiner',
                   assignmentgroup__parentnode=testassignment,
                   relatedexaminer=relatedexaminer2)
        queryset = RelatedExaminer.objects\
            .annotate_with_number_of_groups_on_assignment(assignment=testassignment)
        annotated_relatedexaminer1 = queryset.get(id=relatedexaminer1.id)
        self.assertEqual(
            2, annotated_relatedexaminer1.number_of_groups_on_assignment)
        annotated_relatedexaminer2 = queryset.get(id=relatedexaminer2.id)
        self.assertEqual(
            1, annotated_relatedexaminer2.number_of_groups_on_assignment)


class RelatedExaminerQuerySetExtraAnnotateWithNumberOfCandidatesOnAssignment(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_no_groups(self):
        relatedexaminer = mommy.make('core.RelatedExaminer')
        testassignment = mommy.make('core.Assignment')
        queryset = RelatedExaminer.objects\
            .extra_annotate_with_number_of_candidates_on_assignment(assignment=testassignment)
        annotated_relatedexaminer = queryset.get(id=relatedexaminer.id)
        self.assertEqual(
            0, annotated_relatedexaminer.number_of_candidates_on_assignment)

    def test_only_within_assignment(self):
        relatedexaminer = mommy.make('core.RelatedExaminer')
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup')  # Not within testassignment
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer=relatedexaminer)
        mommy.make('core.Candidate',
                   assignment_group=testgroup)
        queryset = RelatedExaminer.objects\
            .extra_annotate_with_number_of_candidates_on_assignment(assignment=testassignment)
        annotated_relatedexaminer = queryset.get(id=relatedexaminer.id)
        self.assertEqual(
            0, annotated_relatedexaminer.number_of_candidates_on_assignment)

    def test_only_within_assignment_sanity(self):
        relatedexaminer = mommy.make('core.RelatedExaminer')
        testassignment1 = mommy.make('core.Assignment')
        testassignment2 = mommy.make('core.Assignment')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup1,
                   relatedexaminer=relatedexaminer)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup2,
                   relatedexaminer=relatedexaminer)
        mommy.make('core.Candidate',
                   assignment_group=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup2)

        # Test group 1
        queryset = RelatedExaminer.objects\
            .extra_annotate_with_number_of_candidates_on_assignment(assignment=testassignment1)
        annotated_relatedexaminer = queryset.get(id=relatedexaminer.id)
        self.assertEqual(
            1, annotated_relatedexaminer.number_of_candidates_on_assignment)

        # Test group 2
        queryset = RelatedExaminer.objects \
            .extra_annotate_with_number_of_candidates_on_assignment(assignment=testassignment2)
        annotated_relatedexaminer = queryset.get(id=relatedexaminer.id)
        self.assertEqual(
            2, annotated_relatedexaminer.number_of_candidates_on_assignment)

    def test_multiple_candidates(self):
        relatedexaminer = mommy.make('core.RelatedExaminer')
        testassignment = mommy.make('core.Assignment')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup,
                   relatedexaminer=relatedexaminer)
        mommy.make('core.Candidate',
                   assignment_group=testgroup)
        mommy.make('core.Candidate',
                   assignment_group=testgroup)
        queryset = RelatedExaminer.objects\
            .extra_annotate_with_number_of_candidates_on_assignment(assignment=testassignment)
        annotated_relatedexaminer = queryset.get(id=relatedexaminer.id)
        self.assertEqual(
            2, annotated_relatedexaminer.number_of_candidates_on_assignment)

    def test_multiple_examiner_objects(self):
        relatedexaminer = mommy.make('core.RelatedExaminer')
        testassignment = mommy.make('core.Assignment')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup1,
                   relatedexaminer=relatedexaminer)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup2,
                   relatedexaminer=relatedexaminer)
        mommy.make('core.Candidate',
                   assignment_group=testgroup2)
        queryset = RelatedExaminer.objects\
            .extra_annotate_with_number_of_candidates_on_assignment(assignment=testassignment)
        annotated_relatedexaminer = queryset.get(id=relatedexaminer.id)
        self.assertEqual(
            3, annotated_relatedexaminer.number_of_candidates_on_assignment)
