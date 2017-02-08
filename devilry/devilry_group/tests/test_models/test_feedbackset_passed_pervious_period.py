from django.conf import settings
from django.test import TestCase
from model_mommy import mommy

from devilry.apps.core import devilry_core_mommy_factories as core_mommy
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories as group_mommy
from devilry.devilry_group.models import FeedbacksetPassedPreviousPeriod
from devilry.utils.passed_in_previous_period import PassedInPreviousPeriod


class TestFeedbacksetPassedPreviousPeriod(TestCase):

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        self.assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            short_name='cool',
            long_name='imba',
            parentnode__short_name='s15',
            parentnode__long_name='spring 15',
            passing_grade_min_points=10,
            max_points=15
        )
        group1 = mommy.make('core.AssignmentGroup', parentnode=self.assignment, name='group1')
        self.previous_feedbackset = group_mommy.feedbackset_new_attempt_published(group=group1, grading_points=11)
        candidate1 = core_mommy.candidate(group=group1, fullname='Mr. Pomeroy', shortname='mrpomeroy')

        current_assignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            short_name='cool',
            passing_grade_min_points=7,
            max_points=10
        )
        current_group = mommy.make('core.AssignmentGroup', parentnode=current_assignment, name='current_group1')
        mommy.make('core.Candidate', assignment_group=current_group,
                   relatedstudent__user=candidate1.relatedstudent.user)

        self.passed_in_previous = PassedInPreviousPeriod(current_assignment, self.assignment.parentnode)
        candidate_queryset = self.passed_in_previous.get_queryset()
        self.assertEqual(1, candidate_queryset.count())
        self.passed_in_previous.set_passed_in_current_period(candidate_queryset, testuser)

        self.published_feedbackset = AssignmentGroup.objects.get(id=current_group.id) \
            .cached_data.last_published_feedbackset
        self.feedbackset_passed_previous = FeedbacksetPassedPreviousPeriod.objects.filter(
            feedbackset=self.published_feedbackset).first()

    def test_feedbackset_foreign_key_is_correct(self):
        self.assertIsNotNone(self.feedbackset_passed_previous)
        self.assertEqual(self.feedbackset_passed_previous.feedbackset.id, self.published_feedbackset.id)

    def test_assignment_data_is_correct(self):
        self.assertEqual(self.feedbackset_passed_previous.assignment_short_name, self.assignment.short_name)
        self.assertEqual(self.feedbackset_passed_previous.assignment_long_name, self.assignment.long_name)
        self.assertEqual(self.feedbackset_passed_previous.assignment_max_points, self.assignment.max_points)
        self.assertEqual(self.feedbackset_passed_previous.assignment_passing_grade_min_points,
                         self.assignment.passing_grade_min_points)

    def test_period_data_is_correct(self):
        self.assertEqual(self.feedbackset_passed_previous.period_short_name, self.assignment.parentnode.short_name)
        self.assertEqual(self.feedbackset_passed_previous.period_long_name, self.assignment.parentnode.long_name)
        self.assertEqual(self.feedbackset_passed_previous.period_start_time, self.assignment.parentnode.start_time)
        self.assertEqual(self.feedbackset_passed_previous.period_end_time, self.assignment.parentnode.end_time)

    def test_old_grading_data_is_correct(self):
        self.assertEqual(self.feedbackset_passed_previous.grading_points, self.previous_feedbackset.grading_points)
        self.assertEqual(self.feedbackset_passed_previous.grading_published_by,
                         self.previous_feedbackset.grading_published_by)
        self.assertEqual(self.feedbackset_passed_previous.grading_published_datetime,
                         self.previous_feedbackset.grading_published_datetime)

    def test_foreign_key_is_set_to_none_when_feedbackset_is_deleted(self):
        self.published_feedbackset.delete()
        self.assertIsNone(
            FeedbacksetPassedPreviousPeriod.objects.get(id=self.feedbackset_passed_previous.id).feedbackset)
