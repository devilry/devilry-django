import datetime

from django.conf import settings
from django.test import TestCase
from model_bakery import baker

from devilry.apps.core import devilry_core_baker_factories as core_baker
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Candidate
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_baker_factories as group_baker
from devilry.devilry_group.models import FeedbackSet, FeedbacksetPassedPreviousPeriod
from devilry.utils.passed_in_previous_period import PassedInPreviousPeriod, SomeCandidatesDoesNotQualifyToPass


class TestPassedInPreviousPeriodQueryset(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_lol(self):
        user_april = baker.make(settings.AUTH_USER_MODEL, shortname='april')
        user_dewey = baker.make(settings.AUTH_USER_MODEL, shortname='dewey')

        # Setup duck 1010
        subject_duck1010 = baker.make('core.Subject', short_name='duck1010')
        period_duck1010 = baker.make('core.Period',
                                     short_name='period_duck1010',
                                     parentnode=subject_duck1010,
                                     start_time=datetime.datetime(year=2000, month=1, day=1),
                                     end_time=datetime.datetime(year=2005, month=12, day=31))
        assignment_duck1010 = baker.make('core.Assignment', short_name='a', parentnode=period_duck1010)
        group_duck1010 = baker.make('core.AssignmentGroup', parentnode=assignment_duck1010)
        candidate_duck1010 = baker.make('core.Candidate', assignment_group=group_duck1010,
                               relatedstudent__period=period_duck1010, relatedstudent__user=user_april)
        group_baker.feedbackset_first_attempt_published(group=group_duck1010, grading_points=1010)

        # Setup duck 1100
        subject_duck1100 = baker.make('core.Subject', short_name='duck1100')
        period_duck1100 = baker.make('core.Period',
                                     short_name='period_duck1100',
                                     parentnode=subject_duck1100,
                                     start_time=datetime.datetime(year=2006, month=1, day=1),
                                     end_time=datetime.datetime(year=2010, month=12, day=31))
        assignment_duck1100 = baker.make('core.Assignment', short_name='a', parentnode=period_duck1100)
        group1_duck1100 = baker.make('core.AssignmentGroup', parentnode=assignment_duck1100)
        group2_duck1100 = baker.make('core.AssignmentGroup', parentnode=assignment_duck1100)
        candidate_april_duck1100 = baker.make('core.Candidate', assignment_group=group1_duck1100,
                                              relatedstudent__period=period_duck1100, relatedstudent__user=user_april)
        candidate_dewey_duck1100 = baker.make('core.Candidate', assignment_group=group2_duck1100,
                                              relatedstudent__period=period_duck1100, relatedstudent__user=user_dewey)
        group_baker.feedbackset_first_attempt_published(group=group1_duck1100, grading_points=1100)
        group_baker.feedbackset_first_attempt_published(group=group2_duck1100, grading_points=1100)

        # Setup duck 1010 current
        period_duck1010_current = baker.make('core.Period',
                                             short_name='period_duck1010_cur',
                                             parentnode=subject_duck1010,
                                             start_time=datetime.datetime(year=2011, month=1, day=1),
                                             end_time=datetime.datetime(year=2012, month=12, day=31))
        assignment_duck1010_current = baker.make('core.Assignment', short_name='a', parentnode=period_duck1010_current)
        group_duck1010_current = baker.make('core.AssignmentGroup', parentnode=assignment_duck1010_current)
        candidate_duck1010_current = baker.make('core.Candidate', assignment_group=group_duck1010_current,
                               relatedstudent__period=period_duck1010_current, relatedstudent__user=user_april)

        passed_in_previous_queryset = PassedInPreviousPeriod(
            assignment=assignment_duck1010_current, from_period=assignment_duck1010.parentnode).get_queryset()

        self.assertEqual(passed_in_previous_queryset.count(), 1)
        candidate_with_result = passed_in_previous_queryset.first()
        self.assertEqual(candidate_with_result, candidate_duck1010)
        self.assertEqual(candidate_with_result.assignment_group.feedbackset_set.all().first().grading_points, 1010)

    def test_from_period_older_is_ignored(self):
        subject = baker.make('core.Subject')
        assignment1 = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment1)
        group_baker.feedbackset_new_attempt_published(group=group1, grading_points=6)
        candidate1 = core_baker.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        assignment2 = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        group2 = baker.make('core.AssignmentGroup', parentnode=assignment2)
        group_baker.feedbackset_new_attempt_published(group=group2, grading_points=6)
        candidate2 = core_baker.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = baker.make('core.AssignmentGroup', parentnode=assignment2)
        group_baker.feedbackset_new_attempt_published(group=group3, grading_points=6)
        candidate3 = core_baker.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = baker.make_recipe(
            'devilry.apps.core.assignment_futureperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_group1 = baker.make('core.AssignmentGroup', parentnode=current_assignment)
        baker.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_group2 = baker.make('core.AssignmentGroup', parentnode=current_assignment)
        baker.make('core.Candidate', assignment_group=current_group2,
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_group3 = baker.make('core.AssignmentGroup', parentnode=current_assignment)
        baker.make('core.Candidate', assignment_group=current_group3,
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment2.parentnode)
        self.assertListEqual(
            [candidate.relatedstudent.user.get_displayname() for candidate in passed_in_previous.get_queryset()],
            [candidate2.relatedstudent.user.get_displayname(), candidate3.relatedstudent.user.get_displayname()]
        )

    def test_candidates_did_not_pass_in_previous_period(self):
        subject = baker.make('core.Subject')
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment)
        group_baker.feedbackset_new_attempt_published(group=group1, grading_points=4)
        candidate1 = core_baker.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = baker.make('core.AssignmentGroup', parentnode=assignment)
        group_baker.feedbackset_new_attempt_published(group=group2, grading_points=3)
        candidate2 = core_baker.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = baker.make('core.AssignmentGroup', parentnode=assignment)
        group_baker.feedbackset_new_attempt_published(group=group3, grading_points=6)
        candidate3 = core_baker.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_group1 = baker.make('core.AssignmentGroup', parentnode=current_assignment)
        baker.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_group2 = baker.make('core.AssignmentGroup', parentnode=current_assignment)
        baker.make('core.Candidate', assignment_group=current_group2,
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_group3 = baker.make('core.AssignmentGroup', parentnode=current_assignment)
        baker.make('core.Candidate', assignment_group=current_group3,
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        self.assertListEqual(
            [candidate.relatedstudent.user.get_displayname() for candidate in passed_in_previous.get_queryset()],
            [candidate3.relatedstudent.user.get_displayname()]
        )

    def test_no_one_passed_in_pervious_period(self):
        assignment1 = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment1, name='group1')
        group_baker.feedbackset_new_attempt_published(group=group1, grading_points=4)
        candidate1 = core_baker.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        assignment2 = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        group2 = baker.make('core.AssignmentGroup', parentnode=assignment2, name='group2')
        group_baker.feedbackset_new_attempt_published(group=group2, grading_points=3)
        baker.make('core.Candidate', assignment_group=group2,
                   relatedstudent__user=candidate1.relatedstudent.user)

        current_assignment = baker.make_recipe(
            'devilry.apps.core.assignment_futureperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_group1 = baker.make('core.AssignmentGroup', parentnode=current_assignment)
        baker.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment1.parentnode)
        self.assertEqual(0, passed_in_previous.get_queryset().count())

    def test_assignment_name(self):
        subject = baker.make('core.Subject')
        assignment1 = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment1)
        group_baker.feedbackset_new_attempt_published(group=group1, grading_points=5)
        candidate1 = core_baker.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        assignment2 = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            parentnode__parentnode=subject,
            short_name='Imba',
            passing_grade_min_points=5
        )
        group2 = baker.make('core.AssignmentGroup', parentnode=assignment2)
        group_baker.feedbackset_new_attempt_published(group=group1, grading_points=10)
        baker.make('core.Candidate', assignment_group=group2,
                   relatedstudent__user=candidate1.relatedstudent.user)

        current_assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_group1 = baker.make('core.AssignmentGroup', parentnode=current_assignment)
        baker.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment1.parentnode)
        candidate_queryset = passed_in_previous.get_queryset()
        self.assertEqual(1, candidate_queryset.count())
        self.assertEqual(candidate_queryset.first().assignment_group.parentnode.short_name, assignment1.short_name)

    def test_latest_passed_is_used(self):
        subject = baker.make('core.Subject')
        assignment1 = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment1, name='group1')
        group_baker.feedbackset_new_attempt_published(group=group1, grading_points=6)
        candidate1 = core_baker.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        assignment2 = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        group2 = baker.make('core.AssignmentGroup', parentnode=assignment2, name='group2')
        group_baker.feedbackset_new_attempt_published(group=group2, grading_points=10)
        baker.make('core.Candidate', assignment_group=group2,
                   relatedstudent__user=candidate1.relatedstudent.user)

        current_assignment = baker.make_recipe(
            'devilry.apps.core.assignment_futureperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_group1 = baker.make('core.AssignmentGroup', parentnode=current_assignment)
        baker.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment1.parentnode)
        self.assertEqual(1, passed_in_previous.get_queryset().count())
        self.assertEqual(passed_in_previous.get_queryset().first().assignment_group.id, group2.id)

    def test_student_is_on_current_assignment(self):
        subject = baker.make('core.Subject')
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment)
        group_baker.feedbackset_new_attempt_published(group=group1, grading_points=6)
        core_baker.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = baker.make('core.AssignmentGroup', parentnode=assignment)
        group_baker.feedbackset_new_attempt_published(group=group2, grading_points=6)
        core_baker.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = baker.make('core.AssignmentGroup', parentnode=assignment)
        group_baker.feedbackset_new_attempt_published(group=group3, grading_points=6)
        candidate3 = core_baker.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_group3 = baker.make('core.AssignmentGroup', parentnode=current_assignment)
        baker.make('core.Candidate', assignment_group=current_group3,
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        self.assertListEqual(
            [candidate.relatedstudent.user.get_displayname() for candidate in passed_in_previous.get_queryset()],
            [candidate3.relatedstudent.user.get_displayname()]
        )

    def test_candidates_who_got_graded_on_current_assignment_is_filtered_away(self):
        subject = baker.make('core.Subject')
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        group_baker.feedbackset_new_attempt_published(group=group1, grading_points=6)
        candidate1 = core_baker.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        group_baker.feedbackset_new_attempt_published(group=group2, grading_points=6)
        candidate2 = core_baker.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group3')
        group_baker.feedbackset_new_attempt_published(group=group3, grading_points=6)
        candidate3 = core_baker.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_group1 = baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        baker.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_group2 = baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        group_baker.feedbackset_first_attempt_published(group=current_group2, grading_points=7)
        baker.make('core.Candidate', assignment_group=current_group2,
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_group3 = baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        group_baker.feedbackset_first_attempt_published(group=current_group3, grading_points=7)
        baker.make('core.Candidate', assignment_group=current_group3,
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        candidate_queryset = passed_in_previous.get_queryset()
        self.assertEqual(candidate_queryset.count(), 1)
        self.assertEqual(candidate_queryset.first().relatedstudent.user.get_displayname(),
                         candidate1.relatedstudent.user.get_displayname())

    def test_num_queries(self):
        subject = baker.make('core.Subject')
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        group_baker.feedbackset_new_attempt_published(group=group1, grading_points=6)
        candidate1 = core_baker.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        group_baker.feedbackset_new_attempt_published(group=group2, grading_points=6)
        candidate2 = core_baker.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group3')
        group_baker.feedbackset_new_attempt_published(group=group3, grading_points=6)
        candidate3 = core_baker.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_group1 = baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        baker.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_group2 = baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        baker.make('core.Candidate', assignment_group=current_group2,
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_group3 = baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        baker.make('core.Candidate', assignment_group=current_group3,
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        with self.assertNumQueries(1):
            self.assertEqual(3, passed_in_previous.get_queryset().count())


class TestPassedInPreviousPeriodPointConverter(TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_point_converter_1(self):
        assignment1 = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=6,
            max_points=10
        )
        group = baker.make('core.AssignmentGroup', parentnode=assignment1)
        feedbackset = group_baker.feedbackset_first_attempt_published(group=group, grading_points=9)

        assignment2 = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=2,
            max_points=5
        )
        passed_in_previous = PassedInPreviousPeriod(assignment2, assignment1.parentnode)
        grading_points = passed_in_previous.convert_points(feedbackset)
        self.assertEqual(grading_points, 5)

    def test_point_converter_2(self):
        assignment1 = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=3,
            max_points=5
        )
        group = baker.make('core.AssignmentGroup', parentnode=assignment1)
        feedbackset = group_baker.feedbackset_first_attempt_published(group=group, grading_points=3)

        assignment2 = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=10,
            max_points=15
        )
        passed_in_previous = PassedInPreviousPeriod(assignment2, assignment1.parentnode)
        grading_points = passed_in_previous.convert_points(feedbackset)
        self.assertEqual(grading_points, 10)

    def test_point_converter_3(self):
        assignment1 = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=2,
            max_points=3
        )
        group = baker.make('core.AssignmentGroup', parentnode=assignment1)
        feedbackset = group_baker.feedbackset_first_attempt_published(group=group, grading_points=3)

        assignment2 = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=14,
            max_points=20
        )
        passed_in_previous = PassedInPreviousPeriod(assignment2, assignment1.parentnode)
        grading_points = passed_in_previous.convert_points(feedbackset)
        self.assertEqual(grading_points, 20)

    def test_point_converter_4(self):
        assignment1 = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=1,
            max_points=1
        )
        group = baker.make('core.AssignmentGroup', parentnode=assignment1)
        feedbackset = group_baker.feedbackset_first_attempt_published(group=group, grading_points=1)

        assignment2 = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=2,
            max_points=3
        )
        passed_in_previous = PassedInPreviousPeriod(assignment2, assignment1.parentnode)
        grading_points = passed_in_previous.convert_points(feedbackset)
        self.assertEqual(grading_points, 3)


class TestPassedInPreviousPeriod(TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_simple(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        subject = baker.make('core.Subject')
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=10,
            max_points=15
        )
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        previous_feedbackset = group_baker.feedbackset_new_attempt_published(group=group1, grading_points=11)
        candidate1 = core_baker.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        current_assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=7,
            max_points=10
        )
        current_group = baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        baker.make('core.Candidate', assignment_group=current_group,
                   relatedstudent__user=candidate1.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        candidate_queryset = passed_in_previous.get_queryset()
        self.assertEqual(1, candidate_queryset.count())
        passed_in_previous.set_passed_in_current_period(candidate_queryset, testuser)

        published_feedbackset = AssignmentGroup.objects.get(id=current_group.id)\
            .cached_data.last_published_feedbackset
        self.assertIsNotNone(FeedbacksetPassedPreviousPeriod.objects.filter(feedbackset=published_feedbackset).first())
        self.assertIsNotNone(published_feedbackset.grading_published_datetime)
        self.assertEqual(published_feedbackset.grading_published_by, testuser)
        self.assertEqual(published_feedbackset.grading_points, passed_in_previous.convert_points(previous_feedbackset))

    def test_multiple_candidates(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        subject = baker.make('core.Subject')
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        previous_feedbacksets = []
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        previous_feedbacksets.append(group_baker.feedbackset_new_attempt_published(group=group1, grading_points=6))
        candidate1 = core_baker.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        previous_feedbacksets.append(group_baker.feedbackset_new_attempt_published(group=group2, grading_points=6))
        candidate2 = core_baker.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group3')
        previous_feedbacksets.append(group_baker.feedbackset_new_attempt_published(group=group3, grading_points=6))
        candidate3 = core_baker.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_groups = []
        current_groups.append(baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        baker.make('core.Candidate', assignment_group=current_groups[0],
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_groups.append(baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        baker.make('core.Candidate', assignment_group=current_groups[1],
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_groups.append(baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        baker.make('core.Candidate', assignment_group=current_groups[2],
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        candidate_queryset = passed_in_previous.get_queryset()
        passed_in_previous.set_passed_in_current_period(candidate_queryset, testuser)
        published_feedbacksets = FeedbackSet.objects.filter(group__in=current_groups).order_by('id')
        for new_feedbackset, prev_feedbackset in zip(published_feedbacksets, previous_feedbacksets):
            self.assertIsNotNone(
                FeedbacksetPassedPreviousPeriod.objects.filter(feedbackset=new_feedbackset).first())
            self.assertIsNotNone(new_feedbackset.grading_published_datetime)
            self.assertEqual(new_feedbackset.grading_published_by, testuser)
            self.assertEqual(new_feedbackset.grading_points,
                             passed_in_previous.convert_points(prev_feedbackset))

    def test_multiple_candidates_passed_in_a_different_order(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        subject = baker.make('core.Subject')
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        previous_feedbacksets = []
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        previous_feedbacksets.append(group_baker.feedbackset_new_attempt_published(group=group1, grading_points=6))
        candidate1 = core_baker.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        previous_feedbacksets.append(group_baker.feedbackset_new_attempt_published(group=group2, grading_points=6))
        candidate2 = core_baker.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group3')
        previous_feedbacksets.append(group_baker.feedbackset_new_attempt_published(group=group3, grading_points=6))
        candidate3 = core_baker.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_groups = []
        current_groups.append(baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        baker.make('core.Candidate', assignment_group=current_groups[0],
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_groups.append(baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        baker.make('core.Candidate', assignment_group=current_groups[1],
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_groups.append(baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        baker.make('core.Candidate', assignment_group=current_groups[2],
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        candidate_queryset = passed_in_previous.get_queryset().order_by('-relatedstudent__user_id')
        passed_in_previous.set_passed_in_current_period(candidate_queryset, testuser)
        published_feedbacksets = FeedbackSet.objects.filter(group__in=current_groups).order_by('id')
        for new_feedbackset, prev_feedbackset in zip(published_feedbacksets, previous_feedbacksets):
            self.assertIsNotNone(
                FeedbacksetPassedPreviousPeriod.objects.filter(feedbackset=new_feedbackset).first())
            self.assertIsNotNone(new_feedbackset.grading_published_datetime)
            self.assertEqual(new_feedbackset.grading_published_by, testuser)
            self.assertEqual(new_feedbackset.grading_points,
                             passed_in_previous.convert_points(prev_feedbackset))

    def test_some_selected_students_did_not_qualify_to_pass(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        subject = baker.make('core.Subject')
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        previous_feedbacksets = []
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        previous_feedbacksets.append(group_baker.feedbackset_new_attempt_published(group=group1, grading_points=6))
        candidate1 = core_baker.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        previous_feedbacksets.append(group_baker.feedbackset_new_attempt_published(group=group2, grading_points=6))
        candidate2 = core_baker.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group3')
        previous_feedbacksets.append(group_baker.feedbackset_new_attempt_published(group=group3, grading_points=6))
        candidate3 = core_baker.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_groups = []
        current_groups.append(baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        baker.make('core.Candidate', assignment_group=current_groups[0],
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_groups.append(baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        baker.make('core.Candidate', assignment_group=current_groups[1],
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_groups.append(baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        baker.make('core.Candidate', assignment_group=current_groups[2],
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        candidate_queryset = passed_in_previous.get_queryset()
        passed_in_previous.set_passed_in_current_period(candidate_queryset, testuser)
        published_feedbacksets = FeedbackSet.objects.filter(group__in=current_groups).order_by('id')
        for new_feedbackset, prev_feedbackset in zip(published_feedbacksets, previous_feedbacksets):
            self.assertIsNotNone(
                FeedbacksetPassedPreviousPeriod.objects.filter(feedbackset=new_feedbackset).first())
            self.assertIsNotNone(new_feedbackset.grading_published_datetime)
            self.assertEqual(new_feedbackset.grading_published_by, testuser)
            self.assertEqual(new_feedbackset.grading_points,
                             passed_in_previous.convert_points(prev_feedbackset))

    def test_a_selected_student_did_not_pass(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        group_baker.feedbackset_new_attempt_published(group=group1, grading_points=4)
        candidate1 = core_baker.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        group_baker.feedbackset_new_attempt_published(group=group2, grading_points=6)
        candidate2 = core_baker.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group3')
        group_baker.feedbackset_new_attempt_published(group=group3, grading_points=6)
        candidate3 = core_baker.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )

        current_group1 = baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        baker.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_group2 = baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        baker.make('core.Candidate', assignment_group=current_group2,
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_group3 = baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        baker.make('core.Candidate', assignment_group=current_group3,
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        candidate_queryset = Candidate.objects.filter(assignment_group__parentnode=assignment)
        self.assertEqual(3, candidate_queryset.count())
        with self.assertRaises(SomeCandidatesDoesNotQualifyToPass):
            passed_in_previous.set_passed_in_current_period(candidate_queryset, testuser)

    def test_a_selected_student_is_not_part_of_current_assignment(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        group_baker.feedbackset_new_attempt_published(group=group1, grading_points=6)
        candidate1 = core_baker.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        group_baker.feedbackset_new_attempt_published(group=group2, grading_points=6)
        candidate2 = core_baker.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group3')
        group_baker.feedbackset_new_attempt_published(group=group3, grading_points=6)
        core_baker.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )

        current_group1 = baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        baker.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_group2 = baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        baker.make('core.Candidate', assignment_group=current_group2,
                   relatedstudent__user=candidate2.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        candidate_queryset = Candidate.objects.filter(assignment_group__parentnode=assignment)
        self.assertEqual(3, candidate_queryset.count())
        with self.assertRaises(SomeCandidatesDoesNotQualifyToPass):
            passed_in_previous.set_passed_in_current_period(candidate_queryset, testuser)

    def test_a_selected_student_has_never_done_the_previous_assignment(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        assignment2 = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            parentnode=assignment.parentnode,
            short_name='imba'
        )

        group1 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        group_baker.feedbackset_new_attempt_published(group=group1, grading_points=6)
        candidate1 = core_baker.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        group_baker.feedbackset_new_attempt_published(group=group2, grading_points=6)
        candidate2 = core_baker.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = baker.make('core.AssignmentGroup', parentnode=assignment2, name='group3')
        group_baker.feedbackset_new_attempt_published(group=group3, grading_points=6)
        candidate3 = core_baker.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )

        current_group1 = baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        baker.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_group2 = baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        baker.make('core.Candidate', assignment_group=current_group2,
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_group3 = baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        baker.make('core.Candidate', assignment_group=current_group3,
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        candidate_queryset = Candidate.objects.filter(assignment_group__parentnode__parentnode=assignment.period)
        self.assertEqual(3, candidate_queryset.count())
        with self.assertRaises(SomeCandidatesDoesNotQualifyToPass):
            passed_in_previous.set_passed_in_current_period(candidate_queryset, testuser)

    def test_num_queries(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        subject = baker.make('core.Subject')
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        previous_feedbacksets = []
        group1 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        previous_feedbacksets.append(group_baker.feedbackset_new_attempt_published(group=group1, grading_points=6))
        candidate1 = core_baker.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        # group2 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        # previous_feedbacksets.append(group_baker.feedbackset_new_attempt_published(group=group2, grading_points=6))
        # candidate2 = core_baker.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')
        #
        # group3 = baker.make('core.AssignmentGroup', parentnode=assignment, name='group3')
        # previous_feedbacksets.append(group_baker.feedbackset_new_attempt_published(group=group3, grading_points=6))
        # candidate3 = core_baker.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            parentnode__parentnode=subject,
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_groups = []
        current_groups.append(baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        baker.make('core.Candidate', assignment_group=current_groups[0],
                   relatedstudent__user=candidate1.relatedstudent.user)
        # current_groups.append(baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        # baker.make('core.Candidate', assignment_group=current_groups[1],
        #            relatedstudent__user=candidate2.relatedstudent.user)
        # current_groups.append(baker.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        # baker.make('core.Candidate', assignment_group=current_groups[2],
        #            relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        candidate_queryset = passed_in_previous.get_queryset()
        with self.assertNumQueries(16):
            passed_in_previous.set_passed_in_current_period(candidate_queryset, testuser)
