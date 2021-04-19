import mock
from django.contrib import messages
from django.http import Http404
from django.test import TestCase
from django.conf import settings
from django.utils import timezone
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.apps.core import devilry_core_baker_factories as core_baker
from devilry.apps.core.models import Assignment
from devilry.devilry_admin.views.assignment.passed_previous_period import passed_previous_semester_manual
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_baker_factories as group_baker
from devilry.devilry_group.models import FeedbackSet, FeedbacksetPassedPreviousPeriod


class TestPassAssignmentGroupsView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = passed_previous_semester_manual.PassAssignmentGroupsView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mock_crinstance(self):
        mock_crinstance = mock.MagicMock()
        mock_crinstance.get_devilryrole_for_requestuser.return_value = 'departmentadmin'
        return mock_crinstance

    def test_get_selectable_groups(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.AssignmentGroup', parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mock_crinstance()
        )
        self.assertEqual(
            2,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue')
        )

    def test_post_feedback_sanity(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)

        feedbackset = FeedbackSet.objects.get(group=testgroup)
        self.assertIsNone(feedbackset.grading_published_datetime)
        self.assertIsNone(feedbackset.grading_published_by)
        self.assertIsNone(feedbackset.grading_points)

        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mock_crinstance(),
            requestuser=testuser,
            requestkwargs={
                'data': {
                    'feedback_comment_text': 'feedback comment',
                    'selected_items': [testgroup.id]
                }
            }
        )

        self.assertEqual(FeedbacksetPassedPreviousPeriod.objects.count(), 1)
        fbset_passed_previous_period = FeedbacksetPassedPreviousPeriod.objects.get()
        feedbackset = FeedbackSet.objects.get(group=testgroup)
        self.assertEqual(fbset_passed_previous_period.feedbackset, feedbackset)
        self.assertEqual(fbset_passed_previous_period.passed_previous_period_type,
                         FeedbacksetPassedPreviousPeriod.PASSED_PREVIOUS_SEMESTER_TYPES.MANUAL.value)
        self.assertEqual(fbset_passed_previous_period.created_by, testuser)
        self.assertEqual(feedbackset.grading_points, 1)
        self.assertEqual(feedbackset.grading_published_by, testuser)

    def test_post_feedback_for_one_selected_group(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup_1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup_2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)

        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mock_crinstance(),
            requestuser=testuser,
            requestkwargs={
                'data': {
                    'feedback_comment_text': 'feedback comment',
                    'selected_items': [testgroup_1.id]
                }
            }
        )
        self.assertEqual(FeedbacksetPassedPreviousPeriod.objects.count(), 1)

        feedbackset_testgroup_1 = FeedbackSet.objects.get(group=testgroup_1)
        self.assertEqual(feedbackset_testgroup_1.grading_published_by, testuser)
        self.assertEqual(feedbackset_testgroup_1.grading_points, testgroup_1.parentnode.max_points)
        self.assertIsNotNone(feedbackset_testgroup_1.grading_published_datetime)

        feedbackset_testgroup_2 = FeedbackSet.objects.get(group=testgroup_2)
        self.assertIsNone(feedbackset_testgroup_2.grading_published_by)
        self.assertIsNone(feedbackset_testgroup_2.grading_points)
        self.assertIsNone(feedbackset_testgroup_2.grading_published_datetime)

    def test_post_feedback_for_multiple_selected_group(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup_1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup_2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testuser = baker.make(settings.AUTH_USER_MODEL)

        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mock_crinstance(),
            requestuser=testuser,
            requestkwargs={
                'data': {
                    'feedback_comment_text': 'feedback comment',
                    'selected_items': [testgroup_1.id, testgroup_2.id]
                }
            }
        )

        self.assertEqual(FeedbacksetPassedPreviousPeriod.objects.count(), 2)

        feedbackset_testgroup_1 = FeedbackSet.objects.get(group=testgroup_1)
        self.assertEqual(feedbackset_testgroup_1.grading_published_by, testuser)
        self.assertEqual(feedbackset_testgroup_1.grading_points, testgroup_1.parentnode.max_points)
        self.assertIsNotNone(feedbackset_testgroup_1.grading_published_datetime)

        feedbackset_testgroup_2 = FeedbackSet.objects.get(group=testgroup_2)
        self.assertEqual(feedbackset_testgroup_2.grading_published_by, testuser)
        self.assertEqual(feedbackset_testgroup_2.grading_points, testgroup_2.parentnode.max_points)
        self.assertIsNotNone(feedbackset_testgroup_2.grading_published_datetime)

    def test_post_feedback_updates_score_last_feedbackset_is_first_feedbackset(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        grading_time = timezone.now() - timezone.timedelta(days=2)
        group_baker.feedbackset_first_attempt_published(group=testgroup, grading_points=0,
                                                        grading_published_datetime=grading_time)
        testuser = baker.make(settings.AUTH_USER_MODEL)

        feedbackset = testgroup.cached_data.last_feedbackset
        self.assertEqual(feedbackset.grading_points, 0)
        self.assertNotEqual(feedbackset.grading_published_by, testuser)
        self.assertEqual(feedbackset.grading_published_datetime, grading_time)

        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mock_crinstance(),
            requestuser=testuser,
            requestkwargs={
                'data': {
                    'feedback_comment_text': 'feedback comment',
                    'selected_items': [testgroup.id]
                }
            }
        )

        feedbackset = FeedbackSet.objects.get(id=feedbackset.id)
        self.assertEqual(feedbackset.grading_points, testassignment.max_points)
        self.assertEqual(feedbackset.grading_published_by, testuser)
        self.assertTrue(feedbackset.grading_published_datetime > grading_time)

    def test_post_feedback_updates_score_last_feedbackset_is_not_first_feedbackset(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        first_feedbackset_publishing_datetime = timezone.now() - timezone.timedelta(days=2)
        last_feedbackset_publishing_datetime = timezone.now() - timezone.timedelta(days=1)
        group_baker.feedbackset_first_attempt_published(group=testgroup, grading_points=1,
                                                        grading_published_datetime=first_feedbackset_publishing_datetime)
        group_baker.feedbackset_new_attempt_published(group=testgroup, grading_points=0,
                                                      grading_published_datetime=last_feedbackset_publishing_datetime)
        testuser = baker.make(settings.AUTH_USER_MODEL)


        # Test that the first feedbackset is not changed for sanity!
        first_feedbackset = testgroup.cached_data.first_feedbackset
        self.assertEqual(first_feedbackset.grading_points, 1)
        self.assertNotEqual(first_feedbackset.grading_published_by, testuser)
        self.assertEqual(first_feedbackset.grading_published_datetime, first_feedbackset_publishing_datetime)

        # Test the last feedbackset before bulk feedback.
        last_feedbackset = testgroup.cached_data.last_feedbackset
        self.assertEqual(last_feedbackset.grading_points, 0)
        self.assertNotEqual(last_feedbackset.grading_published_by, testuser)
        self.assertEqual(last_feedbackset.grading_published_datetime, last_feedbackset_publishing_datetime)

        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mock_crinstance(),
            requestuser=testuser,
            requestkwargs={
                'data': {
                    'feedback_comment_text': 'feedback comment',
                    'selected_items': [testgroup.id]
                }
            }
        )

        feedbackset = FeedbackSet.objects.get(id=last_feedbackset.id)
        self.assertEqual(feedbackset.grading_points, testassignment.max_points)
        self.assertEqual(feedbackset.grading_published_by, testuser)
        self.assertTrue(feedbackset.grading_published_datetime > last_feedbackset_publishing_datetime)
