from datetime import timedelta

import mock
from django import test
from django.utils import timezone
from model_bakery import baker

from devilry.apps.core.models import Candidate


class TestCandidateQuerySet(test.TestCase):
    def test_filter_has_passing_grade(self):
        testassignment = baker.make('core.Assignment',
                                    passing_grade_min_points=1)
        passingfeecbackset = baker.make('devilry_group.FeedbackSet',
                                        grading_published_datetime=timezone.now(),
                                        group__parentnode=testassignment,
                                        grading_points=1)
        baker.make('devilry_group.FeedbackSet',
                   group__parentnode=testassignment,
                   grading_published_datetime=timezone.now(),
                   grading_points=0)
        testcandidate = baker.make('core.Candidate', assignment_group=passingfeecbackset.group)
        self.assertEqual(
            [testcandidate],
            list(Candidate.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_unpublished_ignored(self):
        testassignment = baker.make('core.Assignment',
                                    passing_grade_min_points=1)
        unpublished_feedbackset = baker.make('devilry_group.FeedbackSet',
                                             grading_published_datetime=None,
                                             group__parentnode=testassignment,
                                             grading_points=1)
        baker.make('core.Candidate', assignment_group=unpublished_feedbackset.group)
        self.assertEqual(
            [],
            list(Candidate.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_unpublished_ignored_but_has_older_published(self):
        testassignment = baker.make('core.Assignment',
                                    passing_grade_min_points=1)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testcandidate = baker.make('core.Candidate', assignment_group=testgroup)
        baker.make('devilry_group.FeedbackSet',
                   group=testgroup,
                   grading_published_datetime=timezone.now() - timedelta(days=2),
                   grading_points=1)
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=None,
                   group=testgroup,
                   grading_points=0)
        self.assertEqual(
            [testcandidate],
            list(Candidate.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_correct_feedbackset_ordering1(self):
        testassignment = baker.make('core.Assignment',
                                    passing_grade_min_points=1)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testcandidate = baker.make('core.Candidate', assignment_group=testgroup)
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=2),
                   group=testgroup,
                   grading_points=0)
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now(),
                   group=testgroup,
                   grading_points=1)
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=3),
                   group=testgroup,
                   grading_points=0)
        self.assertEqual(
            [testcandidate],
            list(Candidate.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_correct_feedbackset_ordering2(self):
        testassignment = baker.make('core.Assignment',
                                    passing_grade_min_points=1)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate', assignment_group=testgroup)
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=2),
                   group=testgroup,
                   grading_points=1)
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now(),
                   group=testgroup,
                   grading_points=0)
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now() - timedelta(days=3),
                   group=testgroup,
                   grading_points=1)
        self.assertEqual(
            [],
            list(Candidate.objects.filter_has_passing_grade(assignment=testassignment)))

    def test_filter_has_passing_grade_not_within_assignment(self):
        testassignment = baker.make('core.Assignment',
                                    passing_grade_min_points=1)
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate', assignment_group=testgroup)
        baker.make('devilry_group.FeedbackSet',
                   grading_published_datetime=timezone.now(),
                   group=testgroup,
                   grading_points=1)
        self.assertEqual(
            [],
            list(Candidate.objects.filter_has_passing_grade(assignment=testassignment)))


class TestCandidateModel(test.TestCase):
    def test_get_anonymous_name_uses_custom_candidate_ids_true_no_candidate_id(self):
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode__uses_custom_candidate_ids=True)
        self.assertEqual('Automatic anonymous ID missing', candidate.get_anonymous_name())

    def test_get_anonymous_name_assignment_argument(self):
        candidate = baker.make('core.Candidate')
        mockassignment = mock.MagicMock()
        mock_uses_custom_candidate_ids = mock.PropertyMock(return_value=True)
        type(mockassignment).uses_custom_candidate_ids = mock_uses_custom_candidate_ids
        candidate.get_anonymous_name(assignment=mockassignment)
        mock_uses_custom_candidate_ids.assert_called_once_with()

    def test_get_anonymous_name_uses_custom_candidate_ids_true_with_candidate_id(self):
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode__uses_custom_candidate_ids=True,
                               candidate_id='MyCandidateId')
        self.assertEqual('MyCandidateId', candidate.get_anonymous_name())

    def test_get_anonymous_name_uses_custom_candidate_ids_false_with_candidate_id(self):
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode__uses_custom_candidate_ids=False,
                               relatedstudent__candidate_id='MyCandidateId')
        self.assertEqual('MyCandidateId', candidate.get_anonymous_name())

    def test_get_anonymous_name_uses_custom_candidate_ids_false_ignores_candidate_candidate_id(self):
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode__uses_custom_candidate_ids=False,
                               candidate_id='ignored',
                               relatedstudent__candidate_id='MyCandidateId')
        self.assertEqual('MyCandidateId', candidate.get_anonymous_name())

    def test_get_anonymous_name_uses_custom_candidate_ids_false_with_anonymous_id(self):
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode__uses_custom_candidate_ids=False,
                               relatedstudent__automatic_anonymous_id='MyAutomaticID')
        self.assertEqual('MyAutomaticID', candidate.get_anonymous_name())

    def test_get_anonymous_name_uses_custom_candidate_ids_false_no_anonymous_id(self):
        candidate = baker.make('core.Candidate',
                               assignment_group__parentnode__uses_custom_candidate_ids=False,
                               relatedstudent__automatic_anonymous_id='')
        self.assertEqual('Automatic anonymous ID missing', candidate.get_anonymous_name())
