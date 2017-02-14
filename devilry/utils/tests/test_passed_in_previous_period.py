from django.conf import settings
from django.test import TestCase
from model_mommy import mommy

from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Candidate
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group.models import FeedbackSet, FeedbacksetPassedPreviousPeriod
from devilry.utils.passed_in_previous_period import PassedInPreviousPeriod, SomeCandidatesDoesNotQualifyToPass


class TestPassedInPreviousPeriodQueryset(TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_from_period_older_is_ignored(self):
        assignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment1)
        group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=6)
        candidate1 = core_mommy.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        assignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment2)
        group_mommy.feedbackset_new_attempt_published(group=group2, grading_points=6)
        candidate2 = core_mommy.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = mommy.make('core.AssignmentGroup', parentnode=assignment2)
        group_mommy.feedbackset_new_attempt_published(group=group3, grading_points=6)
        candidate3 = core_mommy.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_futureperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_group1 = mommy.make('core.AssignmentGroup', parentnode=current_assignment)
        mommy.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_group2 = mommy.make('core.AssignmentGroup', parentnode=current_assignment)
        mommy.make('core.Candidate', assignment_group=current_group2,
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_group3 = mommy.make('core.AssignmentGroup', parentnode=current_assignment)
        mommy.make('core.Candidate', assignment_group=current_group3,
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment2.parentnode)
        self.assertListEqual(
            [candidate.relatedstudent.user.get_displayname() for candidate in passed_in_previous.get_queryset()],
            [candidate2.relatedstudent.user.get_displayname(), candidate3.relatedstudent.user.get_displayname()]
        )

    def test_candidates_did_not_pass_in_previous_period(self):
        assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=4)
        candidate1 = core_mommy.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_new_attempt_published(group=group2, grading_points=3)
        candidate2 = core_mommy.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_new_attempt_published(group=group3, grading_points=6)
        candidate3 = core_mommy.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_group1 = mommy.make('core.AssignmentGroup', parentnode=current_assignment)
        mommy.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_group2 = mommy.make('core.AssignmentGroup', parentnode=current_assignment)
        mommy.make('core.Candidate', assignment_group=current_group2,
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_group3 = mommy.make('core.AssignmentGroup', parentnode=current_assignment)
        mommy.make('core.Candidate', assignment_group=current_group3,
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        self.assertListEqual(
            [candidate.relatedstudent.user.get_displayname() for candidate in passed_in_previous.get_queryset()],
            [candidate3.relatedstudent.user.get_displayname()]
        )

    def test_no_one_passed_in_pervious_period(self):
        assignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment1, name='group1')
        group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=4)
        candidate1 = core_mommy.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        assignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment2, name='group2')
        group_mommy.feedbackset_new_attempt_published(group=group2, grading_points=3)
        mommy.make('core.Candidate', assignment_group=group2,
                   relatedstudent__user=candidate1.relatedstudent.user)

        current_assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_futureperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_group1 = mommy.make('core.AssignmentGroup', parentnode=current_assignment)
        mommy.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment1.parentnode)
        self.assertEqual(0, passed_in_previous.get_queryset().count())

    def test_assignment_name(self):
        assignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment1)
        group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=5)
        candidate1 = core_mommy.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        assignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Imba',
            passing_grade_min_points=5
        )
        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment2)
        group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=10)
        mommy.make('core.Candidate', assignment_group=group2,
                   relatedstudent__user=candidate1.relatedstudent.user)

        current_assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_group1 = mommy.make('core.AssignmentGroup', parentnode=current_assignment)
        mommy.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment1.parentnode)
        candidate_queryset = passed_in_previous.get_queryset()
        self.assertEqual(1, candidate_queryset.count())
        self.assertEqual(candidate_queryset.first().assignment_group.parentnode.short_name, assignment1.short_name)

    def test_latest_passed_is_used(self):
        assignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment1, name='group1')
        group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=6)
        candidate1 = core_mommy.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        assignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment2, name='group2')
        group_mommy.feedbackset_new_attempt_published(group=group2, grading_points=10)
        mommy.make('core.Candidate', assignment_group=group2,
                   relatedstudent__user=candidate1.relatedstudent.user)

        current_assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_futureperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_group1 = mommy.make('core.AssignmentGroup', parentnode=current_assignment)
        mommy.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment1.parentnode)
        self.assertEqual(1, passed_in_previous.get_queryset().count())
        self.assertEqual(passed_in_previous.get_queryset().first().assignment_group.id, group2.id)

    def test_student_is_on_current_assignment(self):
        assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=6)
        core_mommy.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_new_attempt_published(group=group2, grading_points=6)
        core_mommy.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = mommy.make('core.AssignmentGroup', parentnode=assignment)
        group_mommy.feedbackset_new_attempt_published(group=group3, grading_points=6)
        candidate3 = core_mommy.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_group3 = mommy.make('core.AssignmentGroup', parentnode=current_assignment)
        mommy.make('core.Candidate', assignment_group=current_group3,
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        self.assertListEqual(
            [candidate.relatedstudent.user.get_displayname() for candidate in passed_in_previous.get_queryset()],
            [candidate3.relatedstudent.user.get_displayname()]
        )

    def test_candidates_who_got_graded_on_current_assignment_is_filtered_away(self):
        assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=6)
        candidate1 = core_mommy.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        group_mommy.feedbackset_new_attempt_published(group=group2, grading_points=6)
        candidate2 = core_mommy.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group3')
        group_mommy.feedbackset_new_attempt_published(group=group3, grading_points=6)
        candidate3 = core_mommy.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_group1 = mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        mommy.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_group2 = mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        group_mommy.feedbackset_first_attempt_published(group=current_group2, grading_points=7)
        mommy.make('core.Candidate', assignment_group=current_group2,
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_group3 = mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        group_mommy.feedbackset_first_attempt_published(group=current_group3, grading_points=7)
        mommy.make('core.Candidate', assignment_group=current_group3,
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        candidate_queryset = passed_in_previous.get_queryset()
        self.assertEqual(candidate_queryset.count(), 1)
        self.assertEqual(candidate_queryset.first().relatedstudent.user.get_displayname(),
                         candidate1.relatedstudent.user.get_displayname())

    def test_num_queries(self):
        assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=6)
        candidate1 = core_mommy.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        group_mommy.feedbackset_new_attempt_published(group=group2, grading_points=6)
        candidate2 = core_mommy.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group3')
        group_mommy.feedbackset_new_attempt_published(group=group3, grading_points=6)
        candidate3 = core_mommy.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_group1 = mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        mommy.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_group2 = mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        mommy.make('core.Candidate', assignment_group=current_group2,
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_group3 = mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        mommy.make('core.Candidate', assignment_group=current_group3,
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        with self.assertNumQueries(1):
            self.assertEqual(3, passed_in_previous.get_queryset().count())


class TestPassedInPreviousPeriodPointConverter(TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_point_converter_1(self):
        assignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=6,
            max_points=10
        )
        group = mommy.make('core.AssignmentGroup', parentnode=assignment1)
        feedbackset = group_mommy.feedbackset_first_attempt_published(group=group, grading_points=9)

        assignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=2,
            max_points=5
        )
        passed_in_previous = PassedInPreviousPeriod(assignment2, assignment1.parentnode)
        grading_points = passed_in_previous.convert_points(feedbackset)
        self.assertEqual(grading_points, 5)

    def test_point_converter_2(self):
        assignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=3,
            max_points=5
        )
        group = mommy.make('core.AssignmentGroup', parentnode=assignment1)
        feedbackset = group_mommy.feedbackset_first_attempt_published(group=group, grading_points=3)

        assignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=10,
            max_points=15
        )
        passed_in_previous = PassedInPreviousPeriod(assignment2, assignment1.parentnode)
        grading_points = passed_in_previous.convert_points(feedbackset)
        self.assertEqual(grading_points, 10)

    def test_point_converter_3(self):
        assignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=2,
            max_points=3
        )
        group = mommy.make('core.AssignmentGroup', parentnode=assignment1)
        feedbackset = group_mommy.feedbackset_first_attempt_published(group=group, grading_points=3)

        assignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=14,
            max_points=20
        )
        passed_in_previous = PassedInPreviousPeriod(assignment2, assignment1.parentnode)
        grading_points = passed_in_previous.convert_points(feedbackset)
        self.assertEqual(grading_points, 20)

    def test_point_converter_4(self):
        assignment1 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=1,
            max_points=1
        )
        group = mommy.make('core.AssignmentGroup', parentnode=assignment1)
        feedbackset = group_mommy.feedbackset_first_attempt_published(group=group, grading_points=1)

        assignment2 = mommy.make_recipe(
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
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=10,
            max_points=15
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        previous_feedbackset = group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=11)
        candidate1 = core_mommy.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        current_assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=7,
            max_points=10
        )
        current_group = mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        mommy.make('core.Candidate', assignment_group=current_group,
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
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        previous_feedbacksets = []
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        previous_feedbacksets.append(group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=6))
        candidate1 = core_mommy.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        previous_feedbacksets.append(group_mommy.feedbackset_new_attempt_published(group=group2, grading_points=6))
        candidate2 = core_mommy.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group3')
        previous_feedbacksets.append(group_mommy.feedbackset_new_attempt_published(group=group3, grading_points=6))
        candidate3 = core_mommy.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_groups = []
        current_groups.append(mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        mommy.make('core.Candidate', assignment_group=current_groups[0],
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_groups.append(mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        mommy.make('core.Candidate', assignment_group=current_groups[1],
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_groups.append(mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        mommy.make('core.Candidate', assignment_group=current_groups[2],
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
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        previous_feedbacksets = []
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        previous_feedbacksets.append(group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=6))
        candidate1 = core_mommy.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        previous_feedbacksets.append(group_mommy.feedbackset_new_attempt_published(group=group2, grading_points=6))
        candidate2 = core_mommy.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group3')
        previous_feedbacksets.append(group_mommy.feedbackset_new_attempt_published(group=group3, grading_points=6))
        candidate3 = core_mommy.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_groups = []
        current_groups.append(mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        mommy.make('core.Candidate', assignment_group=current_groups[0],
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_groups.append(mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        mommy.make('core.Candidate', assignment_group=current_groups[1],
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_groups.append(mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        mommy.make('core.Candidate', assignment_group=current_groups[2],
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
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        previous_feedbacksets = []
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        previous_feedbacksets.append(group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=6))
        candidate1 = core_mommy.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        previous_feedbacksets.append(group_mommy.feedbackset_new_attempt_published(group=group2, grading_points=6))
        candidate2 = core_mommy.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group3')
        previous_feedbacksets.append(group_mommy.feedbackset_new_attempt_published(group=group3, grading_points=6))
        candidate3 = core_mommy.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_groups = []
        current_groups.append(mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        mommy.make('core.Candidate', assignment_group=current_groups[0],
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_groups.append(mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        mommy.make('core.Candidate', assignment_group=current_groups[1],
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_groups.append(mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        mommy.make('core.Candidate', assignment_group=current_groups[2],
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
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=4)
        candidate1 = core_mommy.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        group_mommy.feedbackset_new_attempt_published(group=group2, grading_points=6)
        candidate2 = core_mommy.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group3')
        group_mommy.feedbackset_new_attempt_published(group=group3, grading_points=6)
        candidate3 = core_mommy.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )

        current_group1 = mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        mommy.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_group2 = mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        mommy.make('core.Candidate', assignment_group=current_group2,
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_group3 = mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        mommy.make('core.Candidate', assignment_group=current_group3,
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        candidate_queryset = Candidate.objects.filter(assignment_group__parentnode=assignment)
        self.assertEqual(3, candidate_queryset.count())
        with self.assertRaises(SomeCandidatesDoesNotQualifyToPass):
            passed_in_previous.set_passed_in_current_period(candidate_queryset, testuser)

    def test_a_selected_student_is_not_part_of_current_assignment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=6)
        candidate1 = core_mommy.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        group_mommy.feedbackset_new_attempt_published(group=group2, grading_points=6)
        candidate2 = core_mommy.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group3')
        group_mommy.feedbackset_new_attempt_published(group=group3, grading_points=6)
        core_mommy.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )

        current_group1 = mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        mommy.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_group2 = mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        mommy.make('core.Candidate', assignment_group=current_group2,
                   relatedstudent__user=candidate2.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        candidate_queryset = Candidate.objects.filter(assignment_group__parentnode=assignment)
        self.assertEqual(3, candidate_queryset.count())
        with self.assertRaises(SomeCandidatesDoesNotQualifyToPass):
            passed_in_previous.set_passed_in_current_period(candidate_queryset, testuser)

    def test_a_selected_student_has_never_done_the_previous_assignment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        assignment2 = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            parentnode=assignment.parentnode,
            short_name='imba'
        )

        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=6)
        candidate1 = core_mommy.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        group2 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        group_mommy.feedbackset_new_attempt_published(group=group2, grading_points=6)
        candidate2 = core_mommy.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')

        group3 = mommy.make('core.AssignmentGroup', parentnode=assignment2, name='group3')
        group_mommy.feedbackset_new_attempt_published(group=group3, grading_points=6)
        candidate3 = core_mommy.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )

        current_group1 = mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        mommy.make('core.Candidate', assignment_group=current_group1,
                   relatedstudent__user=candidate1.relatedstudent.user)
        current_group2 = mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        mommy.make('core.Candidate', assignment_group=current_group2,
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_group3 = mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        mommy.make('core.Candidate', assignment_group=current_group3,
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        candidate_queryset = Candidate.objects.filter(assignment_group__parentnode__parentnode=assignment.period)
        self.assertEqual(3, candidate_queryset.count())
        with self.assertRaises(SomeCandidatesDoesNotQualifyToPass):
            passed_in_previous.set_passed_in_current_period(candidate_queryset, testuser)

    def test_num_queries(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        previous_feedbacksets = []
        group1 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group1')
        previous_feedbacksets.append(group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=6))
        candidate1 = core_mommy.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        # group2 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group2')
        # previous_feedbacksets.append(group_mommy.feedbackset_new_attempt_published(group=group2, grading_points=6))
        # candidate2 = core_mommy.candidate(group=group2, fullname='Mr. Winterbottom', shortname='mrwinterbottom')
        #
        # group3 = mommy.make('core.AssignmentGroup', parentnode=assignment, name='group3')
        # previous_feedbacksets.append(group_mommy.feedbackset_new_attempt_published(group=group3, grading_points=6))
        # candidate3 = core_mommy.candidate(group=group3, fullname='Sir. Toby', shortname='sirtoby')

        current_assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='Cool',
            passing_grade_min_points=5
        )
        current_groups = []
        current_groups.append(mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        mommy.make('core.Candidate', assignment_group=current_groups[0],
                   relatedstudent__user=candidate1.relatedstudent.user)
        # current_groups.append(mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        # mommy.make('core.Candidate', assignment_group=current_groups[1],
        #            relatedstudent__user=candidate2.relatedstudent.user)
        # current_groups.append(mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        # mommy.make('core.Candidate', assignment_group=current_groups[2],
        #            relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        candidate_queryset = passed_in_previous.get_queryset()
        with self.assertNumQueries(16):
            passed_in_previous.set_passed_in_current_period(candidate_queryset, testuser)
