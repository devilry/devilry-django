from django.conf import settings
from django.test import TestCase
from model_mommy import mommy

from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group.models import FeedbackSet
from devilry.utils.passed_in_previous_period import PassedInPreviousPeriod


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

    def test_current_assignment_is_excluded(self):
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
        group_mommy.feedbackset_first_attempt_published(group=current_group1, grading_points=7)
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
        self.assertListEqual(
            [candidate.assignment_group.name for candidate in passed_in_previous.get_queryset()],
            [group1.name, group2.name, group3.name]
        )

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
        passed_in_previous.set_passed_in_current_period(candidate_queryset, testuser)

        published_feedbackset = AssignmentGroup.objects.get(id=current_group.id)\
            .cached_data.last_published_feedbackset
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
            self.assertIsNotNone(new_feedbackset.grading_published_datetime)
            self.assertEqual(new_feedbackset.grading_published_by, testuser)
            self.assertEqual(new_feedbackset.grading_points,
                             passed_in_previous.convert_points(prev_feedbackset))

    def test_only_selected_candidates_will_pass_in_current_period(self):
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
        group_mommy.feedbackset_new_attempt_published(group=group2, grading_points=6)
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
        current_group2 = mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        mommy.make('core.Candidate', assignment_group=current_group2,
                   relatedstudent__user=candidate2.relatedstudent.user)
        current_groups.append(mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1'))
        mommy.make('core.Candidate', assignment_group=current_groups[1],
                   relatedstudent__user=candidate3.relatedstudent.user)

        passed_in_previous = PassedInPreviousPeriod(current_assignment, assignment.parentnode)
        candidate_queryset = passed_in_previous.get_queryset().exclude(id=candidate2.id)
        self.assertEqual(2, candidate_queryset.count())
        passed_in_previous.set_passed_in_current_period(candidate_queryset, testuser)
        published_feedbacksets = FeedbackSet.objects.filter(group__in=current_groups).order_by('id')
        for new_feedbackset, prev_feedbackset in zip(published_feedbacksets, previous_feedbacksets):
            self.assertIsNotNone(new_feedbackset.grading_published_datetime)
            self.assertEqual(new_feedbackset.grading_published_by, testuser)
            self.assertEqual(new_feedbackset.grading_points,
                             passed_in_previous.convert_points(prev_feedbackset))
        self.assertIsNone(AssignmentGroup.objects.get(id=current_group2.id).cached_data.last_published_feedbackset)
        self.assertIsNone(AssignmentGroup.objects.get(
            id=current_group2.id).cached_data.first_feedbackset.grading_published_datetime)

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
        with self.assertNumQueries(14):
            passed_in_previous.set_passed_in_current_period(candidate_queryset, testuser)

# class TestMarkAsPassedInPrevious(TestCase):
#     def setUp(self):
#         self.testhelper = TestHelper()
#
#         # 2 Years ago, student1 and the group with student 2 and 3 passed
#         self.testhelper.add(nodes="uni",
#                             subjects=["sub"],
#                             periods=["p1:begins(-24):ends(6)"],
#                             assignments=["a1"],
#                             assignmentgroups=["stud1:candidate(student1):examiner(examiner1)",
#                                               "stud2:candidate(student2):examiner(examiner1)",
#                                               "stud3and4:candidate(student3,student4):examiner(examiner1)",
#                                               "stud5:candidate(student5):examiner(examiner1)"],
#                             deadlines=['d1:ends(1)'])
#         for group in self.testhelper.sub_p1_a1.assignmentgroups.all():
#             if group.name in ('stud1', 'stud3and4'):
#                 delivery = self.testhelper.add_delivery(group, {"good.py": "print awesome"})
#                 self.testhelper.add_feedback(delivery, {'grade': 'p1Passed', 'points': 100, 'is_passing_grade': True},
#                                              rendered_view='P1 good')
#             else:
#                 delivery = self.testhelper.add_delivery(group, {"bad.py": "print bad"})
#                 self.testhelper.add_feedback(delivery, {'grade': 'p1Failed', 'points': 0, 'is_passing_grade': False})
#
#         # 1 Year ago, student2 and student5 passed
#         self.testhelper.add(nodes="uni",
#                             subjects=["sub"],
#                             periods=["p2:begins(-12):ends(6)"],
#                             assignments=["a1"],
#                             assignmentgroups=["stud1:candidate(student1):examiner(examiner1)",
#                                               "stud2:candidate(student2):examiner(examiner1)",
#                                               "stud3and4:candidate(student3,student4):examiner(examiner1)",
#                                               "stud5:candidate(student5):examiner(examiner1)",
#                                               "studfail:candidate(studentfail):examiner(examiner1)"],
#                             deadlines=['d1:ends(1)'])
#         for group in self.testhelper.sub_p2_a1.assignmentgroups.all():
#             if group.name in ('stud2', 'stud5'):
#                 delivery = self.testhelper.add_delivery(group, {"good.py": "print awesome"})
#                 self.testhelper.add_feedback(delivery, {'grade': 'p2Passed', 'points': 200, 'is_passing_grade': True})
#             else:
#                 delivery = self.testhelper.add_delivery(group, {"bad.py": "print bad"})
#                 self.testhelper.add_feedback(delivery, {'grade': 'p2Failed', 'points': 10, 'is_passing_grade': False})
#
#     def test_mark_group(self):
#         self.testhelper.add(nodes="uni",
#                             subjects=["sub"],
#                             periods=["p3:begins(-2):ends(6)"],
#                             assignments=["a1"],
#                             assignmentgroups=["g1:candidate(student1):examiner(examiner1)"],
#                             deadlines=['d1:ends(1)'])
#         assignment = self.testhelper.sub_p3_a1
#         marker = MarkAsPassedInPreviousPeriod(assignment)
#         group = self.testhelper.sub_p3_a1_g1
#         marker.mark_group(group)
#         delivery = group.deadlines.all()[0].deliveries.all()[0]
#         self.assertEquals(delivery.alias_delivery,
#                           self.testhelper.sub_p1_a1_stud1_d1.deliveries.all()[0])
#         self.assertEquals(delivery.delivery_type, 2) # Alias
#         feedback = delivery.feedbacks.all()[0]
#         self.assertTrue(feedback.is_passing_grade)
#         self.assertEquals(feedback.grade, 'p1Passed')
#         self.assertEquals(feedback.points, 100)
#         self.assertEquals(feedback.rendered_view, 'P1 good')
#
#     def test_mark_group_prioritize_newest(self):
#         self.testhelper.add(nodes="uni",
#                             subjects=["sub"],
#                             periods=["p3:begins(-2):ends(6)"],
#                             assignments=["a1"],
#                             assignmentgroups=["group:candidate(student2):examiner(examiner1)"],
#                             deadlines=['d1:ends(1)'])
#         assignment = self.testhelper.sub_p3_a1
#         marker = MarkAsPassedInPreviousPeriod(assignment)
#         group = self.testhelper.sub_p3_a1_group
#         marker.mark_group(group)
#         delivery = group.deadlines.all()[0].deliveries.all()[0]
#         self.assertEquals(delivery.alias_delivery,
#                           self.testhelper.sub_p2_a1_stud2_d1.deliveries.all()[0])
#
#     def test_mark_group_only_failing_in_previous(self):
#         self.testhelper.add(nodes="uni",
#                             subjects=["sub"],
#                             periods=["p3:begins(-2):ends(6)"],
#                             assignments=["a1"],
#                             assignmentgroups=["group:candidate(studentfail):examiner(examiner1)"],
#                             deadlines=['d1:ends(1)'])
#         assignment = self.testhelper.sub_p3_a1
#         marker = MarkAsPassedInPreviousPeriod(assignment)
#         group = self.testhelper.sub_p3_a1_group
#         with self.assertRaises(OnlyFailingInPrevious):
#             marker.mark_group(group)
#
#     def test_mark_group_not_in_previous(self):
#         self.testhelper.add(nodes="uni",
#                             subjects=["sub"],
#                             periods=["p3:begins(-2):ends(6)"],
#                             assignments=["a1"],
#                             assignmentgroups=["group:candidate(studentnew):examiner(examiner1)"],
#                             deadlines=['d1:ends(1)'])
#         assignment = self.testhelper.sub_p3_a1
#         marker = MarkAsPassedInPreviousPeriod(assignment)
#         group = self.testhelper.sub_p3_a1_group
#         with self.assertRaises(NotInPrevious):
#             marker.mark_group(group)
#
#     def test_mark_multistudent_group_source(self):
#         self.testhelper.add(nodes="uni",
#                             subjects=["sub"],
#                             periods=["p3:begins(-2):ends(6)"],
#                             assignments=["a1"],
#                             assignmentgroups=["group:candidate(student4):examiner(examiner1)"], # Student4 is in a group with student3 on p1.a1
#                             deadlines=['d1:ends(1)'])
#         assignment = self.testhelper.sub_p3_a1
#         marker = MarkAsPassedInPreviousPeriod(assignment)
#         group = self.testhelper.sub_p3_a1_group
#         with self.assertRaises(PassingGradeOnlyInMultiCandidateGroups):
#             marker.mark_group(group)
#
#     def test_mark_group_manually(self):
#         self.testhelper.add(nodes="uni",
#                             subjects=["sub"],
#                             periods=["p3:begins(-2):ends(6)"],
#                             assignments=["a1"],
#                             assignmentgroups=["g1:candidate(student1):examiner(examiner1)"],
#                             deadlines=['d1:ends(1)'])
#         assignment = self.testhelper.sub_p3_a1
#         marker = MarkAsPassedInPreviousPeriod(assignment)
#         group = self.testhelper.sub_p3_a1_g1
#         marker.mark_group(group, feedback={'grade': 'A',
#                                            'is_passing_grade': True,
#                                            'points': 100,
#                                            'rendered_view': 'Test',
#                                            'saved_by': self.testhelper.examiner1})
#         delivery = group.deadlines.all()[0].deliveries.all()[0]
#         self.assertEquals(delivery.alias_delivery, None)
#         self.assertEquals(delivery.delivery_type, 2) # Alias
#         feedback = delivery.feedbacks.all()[0]
#         self.assertTrue(feedback.is_passing_grade)
#         self.assertEquals(feedback.grade, 'A')
#         self.assertEquals(feedback.points, 100)
#         self.assertEquals(feedback.rendered_view, 'Test')
#
#     def test_has_feedback(self):
#         assignment = self.testhelper.sub_p2_a1
#         marker = MarkAsPassedInPreviousPeriod(assignment)
#         group = self.testhelper.sub_p2_a1_stud2
#         with self.assertRaises(HasFeedback):
#             marker.find_previously_passed_group(group)
#
#     def test_mark_all(self):
#         self.testhelper.add(nodes="uni",
#                             subjects=["sub"],
#                             periods=["p3:begins(-2):ends(6)"],
#                             assignments=["a1"],
#                             assignmentgroups=["g1:candidate(student1):examiner(examiner1)",
#                                               "g2:candidate(student2):examiner(examiner1)",
#                                               "g3:candidate(student3):examiner(examiner1)",
#                                               "g4:candidate(student4):examiner(examiner1)",
#                                               "g5:candidate(student5):examiner(examiner1)",
#                                               "g6:candidate(student6):examiner(examiner1)" # student6 is not in any of the previous semesters, and should not be touched
#                                              ],
#                             deadlines=['d1:ends(1)'])
#         assignment = self.testhelper.sub_p3_a1
#         marker = MarkAsPassedInPreviousPeriod(assignment)
#         results = marker.mark_all()
#         self.assertEquals(set(results['marked']),
#                           set([(self.testhelper.sub_p3_a1_g1, self.testhelper.sub_p1_a1_stud1),
#                                (self.testhelper.sub_p3_a1_g2, self.testhelper.sub_p2_a1_stud2),
#                                (self.testhelper.sub_p3_a1_g5, self.testhelper.sub_p2_a1_stud5)]))
#         self.assertEquals(set(results['ignored']['not_in_previous']),
#                           set([self.testhelper.sub_p3_a1_g6]))
#         self.assertEquals(set(results['ignored']['only_multicandidategroups_passed']),
#                           set([self.testhelper.sub_p3_a1_g3,
#                                self.testhelper.sub_p3_a1_g4]))
#         g2 = self.testhelper.sub_p3_a1_g2
#         delivery = g2.deadlines.all()[0].deliveries.all()[0]
#         self.assertEquals(delivery.alias_delivery,
#                           self.testhelper.sub_p2_a1_stud2_d1.deliveries.all()[0])
#
#
#     def test_mark_all_pretend(self):
#         self.testhelper.add(nodes="uni",
#                             subjects=["sub"],
#                             periods=["p3:begins(-2):ends(6)"],
#                             assignments=["a1"],
#                             assignmentgroups=["g1:candidate(student1):examiner(examiner1)",
#                                               "g2:candidate(student2):examiner(examiner1)",
#                                               "g3:candidate(student3):examiner(examiner1)",
#                                               "g4:candidate(student4):examiner(examiner1)",
#                                               "g5:candidate(student5):examiner(examiner1)",
#                                               "g6:candidate(student6):examiner(examiner1)" # student6 is not in any of the previous semesters, and should not be touched
#                                              ],
#                             deadlines=['d1:ends(1)'])
#         assignment = self.testhelper.sub_p3_a1
#         marker = MarkAsPassedInPreviousPeriod(assignment)
#         results = marker.mark_all(pretend=True)
#         self.assertEquals(set(results['marked']),
#                           set([(self.testhelper.sub_p3_a1_g1, self.testhelper.sub_p1_a1_stud1),
#                                (self.testhelper.sub_p3_a1_g2, self.testhelper.sub_p2_a1_stud2),
#                                (self.testhelper.sub_p3_a1_g5, self.testhelper.sub_p2_a1_stud5)]))
#         self.assertEquals(set(results['ignored']['not_in_previous']),
#                           set([self.testhelper.sub_p3_a1_g6]))
#         self.assertEquals(set(results['ignored']['only_multicandidategroups_passed']),
#                           set([self.testhelper.sub_p3_a1_g3,
#                                self.testhelper.sub_p3_a1_g4]))
#         g2 = self.testhelper.sub_p3_a1_g2
#         self.assertEquals(g2.deadlines.all()[0].deliveries.count(), 0)
#
#
#     def test_mark_group_past_deadline(self):
#         self.testhelper.add(nodes="uni",
#                             subjects=["sub"],
#                             periods=["p3:begins(-3):ends(6)"],
#                             assignments=["a1:pub(1)"],
#                             assignmentgroups=["group:candidate(student1):examiner(examiner1)"],
#                             deadlines=['d1:ends(1)'])
#         assignment = self.testhelper.sub_p3_a1
#         marker = MarkAsPassedInPreviousPeriod(assignment)
#         group = self.testhelper.sub_p3_a1_group
#         self.assertEquals(len(group.deadlines.all()), 1)
#         self.assertTrue(group.deadlines.all()[0].deadline < datetime.now())
#         marker.mark_group(group)
#         self.assertEquals(len(group.deadlines.all()), 1)
#         self.assertTrue(group.deadlines.all()[0].deadline >= datetime.now())
