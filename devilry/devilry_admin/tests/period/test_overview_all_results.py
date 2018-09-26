# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import test
from django.utils import timezone

from model_mommy import mommy
import mock

from django_cradmin import cradmin_testhelpers

from devilry.apps.core.models import Assignment, AssignmentGroup
from devilry.devilry_admin.views.period import overview_all_results
from devilry.devilry_dbcache import customsql
from devilry.devilry_group import devilry_group_mommy_factories as group_factory
from devilry.devilry_group.models import GroupComment
from devilry.project.common import settings


class TestOverviewAllResults(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview_all_results.RelatedStudentsAllResultsOverview

    def setUp(self):
        customsql.AssignmentGroupDbCacheCustomSql().initialize()

    def test_title(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertEquals('All students results', mockresponse.selector.one('title').alltext_normalized)

    def test_backlink_exists(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertEqual(1, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
        self.assertEquals(
            mock.call(appname='overview', args=(), viewname='INDEX', kwargs={}),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )

    def test_table_class(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.RelatedStudent', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertTrue(mockresponse.selector.one('.devilry-tabulardata-list'))

    def test_table_no_students(self):
        testperiod = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=testuser
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-tabulardata-list'))
        self.assertEquals(
            'No students on period',
            mockresponse.selector.one('.django-cradmin-listbuilderview-no-items-message').alltext_normalized)

    def test_table_results_points_passed(self):
        testperiod = mommy.make('core.Period')
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testperiod)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_published(group=testgroup, grading_points=1)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=requestuser
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-overview-all-results-result-cell'))
        self.assertEqual(mockresponse.selector.one('.devilry-core-grade-full').alltext_normalized, 'passed (1/1)')

    def test_table_results_points_failed(self):
        testperiod = mommy.make('core.Period')
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testperiod)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_published(group=testgroup, grading_points=0)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=requestuser
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-overview-all-results-result-cell'))
        self.assertEqual(mockresponse.selector.one('.devilry-core-grade-full').alltext_normalized, 'failed (0/1)')

    def test_table_results_not_registered_on_assignment(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.Assignment', parentnode=testperiod)
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.RelatedStudent', period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=requestuser
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-overview-all-results-result-cell'))
        self.assertEqual(mockresponse.selector.one('.devilry-overview-all-results-result-cell').alltext_normalized,
                         'Not registered')

    def test_table_results_waiting_for_deliveries(self):
        testperiod = mommy.make('core.Period')
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testperiod)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() + timezone.timedelta(days=1))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=requestuser
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-overview-all-results-result-cell'))
        self.assertEqual(mockresponse.selector.one('.devilry-overview-all-results-result-cell').alltext_normalized,
                         'Waiting for deliveries')

    def test_table_results_waiting_for_feedback(self):
        testperiod = mommy.make('core.Period')
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testperiod)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() - timezone.timedelta(days=1))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=requestuser
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-overview-all-results-result-cell'))
        self.assertEqual(mockresponse.selector.one('.devilry-overview-all-results-result-cell').alltext_normalized,
                         'Waiting for feedback')

    def test_table_hard_deadline_results_no_deliveries(self):
        testperiod = mommy.make('core.Period')
        testassignment = mommy.make('core.Assignment', parentnode=testperiod,
                                    deadline_handling=Assignment.DEADLINEHANDLING_HARD)
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testperiod)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        group_factory.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() - timezone.timedelta(days=1))
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=requestuser
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-overview-all-results-result-cell'))
        self.assertEqual(mockresponse.selector.one('.devilry-overview-all-results-result-cell').alltext_normalized,
                         'No deliveries')

    def test_table_hard_deadline_results_comment_from_student_waiting_for_feedback(self):
        testperiod = mommy.make('core.Period')
        testassignment = mommy.make('core.Assignment', parentnode=testperiod,
                                    deadline_handling=Assignment.DEADLINEHANDLING_HARD)
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        relatedstudent = mommy.make('core.RelatedStudent', period=testperiod)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate', assignment_group=testgroup, relatedstudent=relatedstudent)
        feedbackset = group_factory.feedbackset_first_attempt_unpublished(
            group=testgroup, deadline_datetime=timezone.now() - timezone.timedelta(days=1))
        mommy.make('devilry_group.GroupComment', user=relatedstudent.user,
                   user_role=GroupComment.USER_ROLE_STUDENT,
                   text='asd',
                   published_datetime=timezone.now() - timezone.timedelta(days=1, hours=1),
                   feedback_set=feedbackset)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testperiod,
            requestuser=requestuser
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-overview-all-results-result-cell'))
        self.assertEqual(mockresponse.selector.one('.devilry-overview-all-results-result-cell').alltext_normalized,
                         'Waiting for feedback')
