from datetime import timedelta

from django import test
from django.utils import timezone
from model_mommy import mommy

from devilry.apps.core.models import Candidate


class TestCandidateQuerySet(test.TestCase):
    def test_filter_has_passing_grade(self):
        testassignment = mommy.make('core.Assignment',
                                    passing_grade_min_points=1)
        passingfeecbackset = mommy.make('devilry_group.FeedbackSet',
                                        grading_published_datetime=timezone.now(),
                                        is_last_in_group=None,
                                        group__parentnode=testassignment,
                                        grading_points=1)
        mommy.make('devilry_group.FeedbackSet',
                   group__parentnode=testassignment,
                   grading_published_datetime=timezone.now(),
                   grading_points=0)
        testcandidate = mommy.make('core.Candidate', assignment_group=passingfeecbackset.group)
        self.assertEqual(
            [testcandidate],
            list(Candidate.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_unpublished_ignored(self):
        testassignment = mommy.make('core.Assignment',
                                    passing_grade_min_points=1)
        unpublished_feedbackset = mommy.make('devilry_group.FeedbackSet',
                                             grading_published_datetime=None,
                                             group__parentnode=testassignment,
                                             grading_points=1)
        mommy.make('core.Candidate', assignment_group=unpublished_feedbackset.group)
        self.assertEqual(
            [],
            list(Candidate.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_unpublished_ignored_but_has_older_published(self):
        testassignment = mommy.make('core.Assignment',
                                    passing_grade_min_points=1)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testcandidate = mommy.make('core.Candidate', assignment_group=testgroup)
        mommy.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   is_last_in_group=None,
                   grading_published_datetime=timezone.now() - timedelta(days=2),
                   grading_points=1)
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=None,
                   group=testgroup,
                   grading_points=0)
        self.assertEqual(
            [testcandidate],
            list(Candidate.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_correct_feedbackset_ordering1(self):
        testassignment = mommy.make('core.Assignment',
                                    passing_grade_min_points=1)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testcandidate = mommy.make('core.Candidate', assignment_group=testgroup)
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=2),
                   group=testgroup,
                   is_last_in_group=None,
                   grading_points=0)
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now(),
                   group=testgroup,
                   is_last_in_group=None,
                   grading_points=1)
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=3),
                   group=testgroup,
                   grading_points=0)
        self.assertEqual(
            [testcandidate],
            list(Candidate.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_correct_feedbackset_ordering2(self):
        testassignment = mommy.make('core.Assignment',
                                    passing_grade_min_points=1)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup)
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=2),
                   group=testgroup,
                   is_last_in_group=None,
                   grading_points=1)
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now(),
                   group=testgroup,
                   is_last_in_group=None,
                   grading_points=0)
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=3),
                   group=testgroup,
                   grading_points=1)
        self.assertEqual(
            [],
            list(Candidate.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_not_within_assignment(self):
        testassignment = mommy.make('core.Assignment',
                                    passing_grade_min_points=1)
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate', assignment_group=testgroup)
        mommy.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now(),
                   group=testgroup,
                   grading_points=1)
        self.assertEqual(
            [],
            list(Candidate.objects.filter_has_passing_grade(assignment=testassignment)))
