# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
from django import http
from django import test
from django.contrib import messages
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_dbcache import customsql
from devilry.devilry_dbcache import models as cache_models
from devilry.devilry_deadlinemanagement.views import multiselect_groups_view
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group import models as group_models
from devilry.project.common import settings
from devilry.apps.core import models as core_models
from devilry.utils import datetimeutils


class TestExaminerBulkAddNewAttempt(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = multiselect_groups_view.MoveDeadlineManualGroupSelectView

    def setUp(self):
        customsql.AssignmentGroupDbCacheCustomSql().initialize()

    def __get_mock_app(self, user=None):
        mock_app = mock.MagicMock()
        mock_app.get_devilryrole.return_value = 'examiner'
        mock_app.get_accessible_group_queryset.return_value = core_models.AssignmentGroup.objects\
            .filter_examiner_has_access(user=user)
        return mock_app

    def test_title(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            cradmin_app=self.__get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                'handle_deadline': 'move-deadline'
            })
        self.assertIn(
            'Select groups',
            mockresponse.selector.one('title').alltext_normalized)

    def test_anonymizationmode_off_candidates(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='unanonymizedfullname',
                   relatedstudent__user__fullname='A un-anonymized fullname',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            cradmin_app=self.__get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                'handle_deadline': 'move-deadline'
            }
        )
        self.assertIn('unanonymizedfullname', mockresponse.response.content)
        self.assertIn('A un-anonymized fullname', mockresponse.response.content)
        self.assertNotIn('MyAnonymousID', mockresponse.response.content)

    def test_anonymizationmode_semi_anonymous_candidates(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='unanonymizedfullname',
                   relatedstudent__user__fullname='A un-anonymized fullname',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            cradmin_app=self.__get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                'handle_deadline': 'move-deadline'
            }
        )
        self.assertNotIn('unanonymizedfullname', mockresponse.response.content)
        self.assertNotIn('A un-anonymized fullname', mockresponse.response.content)
        self.assertIn('MyAnonymousID', mockresponse.response.content)

    def test_anonymizationmode_fully_anonymous_candidates(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='unanonymizedfullname',
                   relatedstudent__user__fullname='A un-anonymized fullname',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            cradmin_app=self.__get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                'handle_deadline': 'move-deadline'
            }
        )
        self.assertNotIn('unanonymizedfullname', mockresponse.response.content)
        self.assertNotIn('A un-anonymized fullname', mockresponse.response.content)
        self.assertIn('MyAnonymousID', mockresponse.response.content)

    def test_search_anonymous_nomatch_fullname(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUser')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'move-deadline',
                    'filters_string': 'search-TestUser'
                })
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_nomatch_shortname(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='testuser')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'move-deadline',
                    'filters_string': 'search-testuser'
                })
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_nomatch_candidate_id_from_candidate(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   candidate_id='MyCandidateID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'move-deadline',
                    'filters_string': 'search-MyCandidateID'
                })
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_match_automatic_candidate_id_from_relatedstudent(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__candidate_id='MyCandidateID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'move-deadline',
                    'filters_string': 'search-MyCandidateID'
                })
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_match_automatic_anonymous_id(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'move-deadline',
                    'filters_string': 'search-MyAnonymousID'
                })
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_fullname(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUser')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'move-deadline',
                    'filters_string': 'search-TestUser'
                })
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_shortname(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='testuser')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'move-deadline',
                    'filters_string': 'search-testuser'
                })
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_automatic_candidate_id_from_relatedstudent(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__candidate_id='MyCandidateID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'move-deadline',
                    'filters_string': 'search-MyCandidateID'
                })
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_automatic_anonymous_id(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'move-deadline',
                    'filters_string': 'search-MyAnonymousID'
                })
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_match_candidate_id_from_candidate(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   candidate_id='MyCandidateID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'move-deadline',
                    'filters_string': 'search-MyCandidateID'
                })
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_three_groups_on_assignment_published(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup3)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            cradmin_app=self.__get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                'handle_deadline': 'move-deadline'
            })
        self.assertEquals(
            3,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_get_num_queries(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup3)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3,
                   relatedexaminer__user=examiner_user)
        with self.assertNumQueries(5):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                    'handle_deadline': 'move-deadline'
                })

    def test_post_num_queries(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup3)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3,
                   relatedexaminer__user=examiner_user)

        with self.assertNumQueries(3):
            self.mock_http302_postrequest(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                    'handle_deadline': 'move-deadline'
                },
                requestkwargs={
                    'data': {
                        'selected_items': [testgroup1.id, testgroup2.id, testgroup3.id]
                    }
                })


class TestExaminerNewAttemptMultiSelectView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = multiselect_groups_view.NewAttemptManualGroupSelectView

    def setUp(self):
        customsql.AssignmentGroupDbCacheCustomSql().initialize()

    def __get_mock_app(self, user=None):
        mock_app = mock.MagicMock()
        mock_app.get_devilryrole.return_value = 'examiner'
        mock_app.get_accessible_group_queryset.return_value = core_models.AssignmentGroup.objects\
            .filter_examiner_has_access(user=user)
        return mock_app

    def test_title(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            cradmin_app=self.__get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                'handle_deadline': 'new-attempt'
            })
        self.assertIn(
            'Select groups',
            mockresponse.selector.one('title').alltext_normalized)

    def test_anonymizationmode_off_candidates(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='unanonymizedfullname',
                   relatedstudent__user__fullname='A un-anonymized fullname',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            cradmin_app=self.__get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                'handle_deadline': 'new-attempt'
            }
        )
        self.assertIn('unanonymizedfullname', mockresponse.response.content)
        self.assertIn('A un-anonymized fullname', mockresponse.response.content)
        self.assertNotIn('MyAnonymousID', mockresponse.response.content)

    def test_anonymizationmode_semi_anonymous_candidates(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='unanonymizedfullname',
                   relatedstudent__user__fullname='A un-anonymized fullname',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            cradmin_app=self.__get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                'handle_deadline': 'new-attempt'
            }
        )
        self.assertNotIn('unanonymizedfullname', mockresponse.response.content)
        self.assertNotIn('A un-anonymized fullname', mockresponse.response.content)
        self.assertIn('MyAnonymousID', mockresponse.response.content)

    def test_anonymizationmode_fully_anonymous_candidates(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='unanonymizedfullname',
                   relatedstudent__user__fullname='A un-anonymized fullname',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            cradmin_app=self.__get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                'handle_deadline': 'new-attempt'
            }
        )
        self.assertNotIn('unanonymizedfullname', mockresponse.response.content)
        self.assertNotIn('A un-anonymized fullname', mockresponse.response.content)
        self.assertIn('MyAnonymousID', mockresponse.response.content)

    def test_search_anonymous_nomatch_fullname(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUser')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'new-attempt',
                    'filters_string': 'search-TestUser'
                })
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_nomatch_shortname(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='testuser')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'new-attempt',
                    'filters_string': 'search-testuser'
                })
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_nomatch_candidate_id_from_candidate(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   candidate_id='MyCandidateID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'new-attempt',
                    'filters_string': 'search-MyCandidateID'
                })
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_match_automatic_candidate_id_from_relatedstudent(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__candidate_id='MyCandidateID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'new-attempt',
                    'filters_string': 'search-MyCandidateID'
                })
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_match_automatic_anonymous_id(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'new-attempt',
                    'filters_string': 'search-MyAnonymousID'
                })
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_fullname(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUser')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'new-attempt',
                    'filters_string': 'search-TestUser'
                })
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_shortname(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='testuser')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'new-attempt',
                    'filters_string': 'search-testuser'
                })
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_automatic_candidate_id_from_relatedstudent(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__candidate_id='MyCandidateID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'new-attempt',
                    'filters_string': 'search-MyCandidateID'
                })
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_automatic_anonymous_id(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'new-attempt',
                    'filters_string': 'search-MyAnonymousID'
                })
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_match_candidate_id_from_candidate(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examiner_user,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   candidate_id='MyCandidateID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
            'handle_deadline': 'new-attempt',
                    'filters_string': 'search-MyCandidateID'
                })
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_three_groups_on_assignment_published(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup3)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            cradmin_app=self.__get_mock_app(examiner_user),
            viewkwargs={
                'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                'handle_deadline': 'new-attempt'
            })
        self.assertEquals(
            3,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_post_raise_404(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        with self.assertRaises(http.Http404):
            self.mock_http302_postrequest(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                    'handle_deadline': 'new-attempt',
                },
                requestkwargs={
                    'data': {
                        'selected_items': [testgroup1.id, testgroup2.id]
                    }
                })

    def test_get_num_queries(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup3)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3,
                   relatedexaminer__user=examiner_user)
        with self.assertNumQueries(6):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                    'handle_deadline': 'new-attempt'
                })

    def test_post_num_queries(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup3)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3,
                   relatedexaminer__user=examiner_user)

        with self.assertNumQueries(4):
            self.mock_http302_postrequest(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                cradmin_app=self.__get_mock_app(examiner_user),
                viewkwargs={
                    'deadline': datetimeutils.datetime_to_string(testassignment.first_deadline),
                    'handle_deadline': 'new-attempt'
                },
                requestkwargs={
                    'data': {
                        'selected_items': [testgroup1.id, testgroup2.id, testgroup3.id]
                    }
                })