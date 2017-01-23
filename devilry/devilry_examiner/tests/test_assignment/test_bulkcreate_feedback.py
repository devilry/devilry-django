from django import test

from model_mommy import mommy
import mock

from django_cradmin import cradmin_testhelpers
from devilry.devilry_group import models as group_models
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_examiner.views.assignment import bulk_feedback
from devilry.devilry_dbcache import customsql
from devilry.devilry_dbcache import models as cache_models
from devilry.project.common import settings
from devilry.apps.core import models as core_models


class TestPassedFailedBulkCreateFeedback(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = bulk_feedback.BulkFeedbackPassedFailedView

    def setUp(self):
        customsql.AssignmentGroupDbCacheCustomSql().initialize()

    def test_only_bulk_create_passed_group_ids(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        # create assignment group
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)

        # create examiner for group
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)

        # create FeedbackSets for the AssignmentGroups
        testfeedbackset_first_attempt = devilry_group_mommy_factories\
            .feedbackset_first_attempt_published(group=testgroup1)
        testfeedbackset_new_attempt = devilry_group_mommy_factories\
            .feedbackset_new_attempt_unpublished(group=testgroup1)
        devilry_group_mommy_factories \
            .feedbackset_new_attempt_unpublished(group=testgroup2)

        self.mock_postrequest(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            requestkwargs={
                'data': {
                    'passed': True,
                    'feedback_comment_text': 'feedback comment',
                    'selected_items': [testgroup1.id]
                }
            }
        )

        cached_data_group1 = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup1)
        self.assertNotEquals(testfeedbackset_first_attempt, cached_data_group1.last_published_feedbackset)
        self.assertEquals(testfeedbackset_new_attempt, cached_data_group1.last_published_feedbackset)
        self.assertEquals(1, group_models.GroupComment.objects.count())

        cached_data_group2 = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup2)
        self.assertIsNone(cached_data_group2.last_published_feedbackset)

    def test_group_receives_bulk_feedback(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        # create assignment group
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)

        # create examiner for group
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=examiner_user)

        # create feedbacksets for the groups
        testfeedbackset_first_attempt = devilry_group_mommy_factories\
            .feedbackset_first_attempt_published(group=testgroup)
        testfeedbackset_new_attempt = devilry_group_mommy_factories\
            .feedbackset_new_attempt_unpublished(group=testgroup)

        self.mock_postrequest(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            requestkwargs={
                'data': {
                    'passed': True,
                    'feedback_comment_text': 'feedback comment',
                    'selected_items': [testgroup.id]
                }
            }
        )

        cached_data = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup)
        self.assertNotEquals(testfeedbackset_first_attempt, cached_data.last_published_feedbackset)
        self.assertEquals(testfeedbackset_new_attempt, cached_data.last_published_feedbackset)
        self.assertEquals(1, group_models.GroupComment.objects.count())
        comment = group_models.GroupComment.objects.all()[0]
        self.assertEquals('feedback comment', comment.text)
        self.assertEquals(testassignment.passing_grade_min_points,
                          cached_data.last_published_feedbackset.grading_points)

    def test_multiple_groups_receive_bulk_feedback(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        # create AssignmentGroups
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)

        # create user as examiner for AssignmentGroups
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=examiner_user)

        # create feedbacksets for the groups
        testfeedbackset_group1 = devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup1)
        testfeedbackset_group2 = devilry_group_mommy_factories \
            .feedbackset_first_attempt_unpublished(group=testgroup2)
        testfeedbackset_group3 = devilry_group_mommy_factories \
            .feedbackset_first_attempt_unpublished(group=testgroup3)

        self.mock_postrequest(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            requestkwargs={
                'data': {
                    'passed': True,
                    'feedback_comment_text': 'feedback comment',
                    'selected_items': [testgroup1.id, testgroup2.id, testgroup3.id]
                }
            }
        )

        # Test cached data.
        cached_data_group1 = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup1)
        cached_data_group2 = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup2)
        cached_data_group3 = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup3)
        self.assertEquals(testfeedbackset_group1, cached_data_group1.last_published_feedbackset)
        self.assertEquals(testfeedbackset_group2, cached_data_group2.last_published_feedbackset)
        self.assertEquals(testfeedbackset_group3, cached_data_group3.last_published_feedbackset)

        # Test bulk created GroupComments
        group_comments = group_models.GroupComment.objects.all()
        self.assertEquals(3, group_comments.count())
        for group_comment in group_comments:
            self.assertEquals('feedback comment', group_comment.text)

        # Test bulk created FeedbackSets
        feedback_sets = group_models.FeedbackSet.objects.all()
        self.assertEquals(3, feedback_sets.count())
        for feedback_set in feedback_sets:
            self.assertIsNotNone(feedback_set.grading_published_datetime)
            self.assertEquals(feedback_set.grading_points, testassignment.passing_grade_min_points)


class TestPointsBulkCreateFeedback(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = bulk_feedback.BulkFeedbackPointsView

    def setUp(self):
        customsql.AssignmentGroupDbCacheCustomSql().initialize()

    def test_only_bulk_create_passed_group_ids(self):
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
            passing_grade_min_points=6,
            max_points=10)

        # create assignment group
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)

        # create examiner for group
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)

        # create FeedbackSets for the AssignmentGroups
        testfeedbackset_first_attempt = devilry_group_mommy_factories\
            .feedbackset_first_attempt_published(group=testgroup1)
        testfeedbackset_new_attempt = devilry_group_mommy_factories\
            .feedbackset_new_attempt_unpublished(group=testgroup1)
        devilry_group_mommy_factories \
            .feedbackset_new_attempt_unpublished(group=testgroup2)

        self.mock_postrequest(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            requestkwargs={
                'data': {
                    'points': 10,
                    'feedback_comment_text': 'feedback comment',
                    'selected_items': [testgroup1.id]
                }
            }
        )

        cached_data_group1 = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup1)
        self.assertNotEquals(testfeedbackset_first_attempt, cached_data_group1.last_published_feedbackset)
        self.assertEquals(testfeedbackset_new_attempt, cached_data_group1.last_published_feedbackset)
        self.assertEquals(1, group_models.GroupComment.objects.count())

        cached_data_group2 = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup2)
        self.assertIsNone(cached_data_group2.last_published_feedbackset)

    def test_group_receives_bulk_feedback(self):
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
            passing_grade_min_points=6,
            max_points=10)

        # create assignment group
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)

        # create examiner for group
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=examiner_user)

        # create feedbacksets for the groups
        testfeedbackset_first_attempt = devilry_group_mommy_factories\
            .feedbackset_first_attempt_published(group=testgroup)
        testfeedbackset_new_attempt = devilry_group_mommy_factories\
            .feedbackset_new_attempt_unpublished(group=testgroup)

        self.mock_postrequest(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            requestkwargs={
                'data': {
                    'points': 10,
                    'feedback_comment_text': 'feedback comment',
                    'selected_items': [testgroup.id]
                }
            }
        )

        cached_data = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup)
        self.assertNotEquals(testfeedbackset_first_attempt, cached_data.last_published_feedbackset)
        self.assertEquals(testfeedbackset_new_attempt, cached_data.last_published_feedbackset)
        self.assertEquals(1, group_models.GroupComment.objects.count())
        comment = group_models.GroupComment.objects.all()[0]
        self.assertEquals('feedback comment', comment.text)
        self.assertEquals(10, cached_data.last_published_feedbackset.grading_points)

    def test_multiple_groups_receive_bulk_feedback(self):
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
            passing_grade_min_points=6,
            max_points=10)

        # create AssignmentGroups
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)

        # create user as examiner for AssignmentGroups
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=examiner_user)

        # create feedbacksets for the groups
        testfeedbackset_group1 = devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup1)
        testfeedbackset_group2 = devilry_group_mommy_factories \
            .feedbackset_first_attempt_unpublished(group=testgroup2)
        testfeedbackset_group3 = devilry_group_mommy_factories \
            .feedbackset_first_attempt_unpublished(group=testgroup3)

        self.mock_postrequest(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            requestkwargs={
                'data': {
                    'points': 10,
                    'feedback_comment_text': 'feedback comment',
                    'selected_items': [testgroup1.id, testgroup2.id, testgroup3.id]
                }
            }
        )

        # Test cached data.
        cached_data_group1 = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup1)
        cached_data_group2 = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup2)
        cached_data_group3 = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup3)
        self.assertEquals(testfeedbackset_group1, cached_data_group1.last_published_feedbackset)
        self.assertEquals(testfeedbackset_group2, cached_data_group2.last_published_feedbackset)
        self.assertEquals(testfeedbackset_group3, cached_data_group3.last_published_feedbackset)

        # Test bulk created GroupComments
        group_comments = group_models.GroupComment.objects.all()
        self.assertEquals(3, group_comments.count())
        for group_comment in group_comments:
            self.assertEquals('feedback comment', group_comment.text)

        # Test bulk created FeedbackSets
        feedback_sets = group_models.FeedbackSet.objects.all()
        self.assertEquals(3, feedback_sets.count())
        for feedback_set in feedback_sets:
            self.assertIsNotNone(feedback_set.grading_published_datetime)
            self.assertEquals(10, feedback_set.grading_points)

    # def test_num_queries(self):
    #     testassignment = mommy.make_recipe(
    #         'devilry.apps.core.assignment_activeperiod_start',
    #         grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
    #         passing_grade_min_points=6,
    #         max_points=10)
    #
    #     # create AssignmentGroups
    #     testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
    #     testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
    #     testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
    #
    #     # create user as examiner for AssignmentGroups
    #     examiner_user = mommy.make(settings.AUTH_USER_MODEL)
    #     mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)
    #     mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=examiner_user)
    #     mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=examiner_user)
    #
    #     # create feedbacksets for the groups
    #     testfeedbackset_group1 = devilry_group_mommy_factories\
    #         .feedbackset_first_attempt_unpublished(group=testgroup1)
    #     testfeedbackset_group2 = devilry_group_mommy_factories \
    #         .feedbackset_first_attempt_unpublished(group=testgroup2)
    #     testfeedbackset_group3 = devilry_group_mommy_factories \
    #         .feedbackset_first_attempt_unpublished(group=testgroup3)
    #
    #     with self.assertNumQueries(10):
    #         self.mock_postrequest(
    #             cradmin_role=testassignment,
    #             requestuser=examiner_user,
    #             requestkwargs={
    #                 'data': {
    #                     'points': 10,
    #                     'feedback_comment_text': 'feedback comment',
    #                     'selected_items': [testgroup1.id, testgroup2.id, testgroup3.id]
    #                 }
    #             }
    #         )
    #
    #     # Test cached data.
    #     cached_data_group1 = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup1)
    #     cached_data_group2 = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup2)
    #     cached_data_group3 = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup3)
    #     self.assertEquals(testfeedbackset_group1, cached_data_group1.last_published_feedbackset)
    #     self.assertEquals(testfeedbackset_group2, cached_data_group2.last_published_feedbackset)
    #     self.assertEquals(testfeedbackset_group3, cached_data_group3.last_published_feedbackset)
    #
    #     # Test bulk created GroupComments
    #     group_comments = group_models.GroupComment.objects.all()
    #     self.assertEquals(3, group_comments.count())
    #     for group_comment in group_comments:
    #         self.assertEquals('feedback comment', group_comment.text)
    #
    #     # Test bulk created FeedbackSets
    #     feedback_sets = group_models.FeedbackSet.objects.all()
    #     self.assertEquals(3, feedback_sets.count())
    #     for feedback_set in feedback_sets:
    #         self.assertIsNotNone(feedback_set.grading_published_datetime)
    #         self.assertEquals(10, feedback_set.grading_points)

