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
from devilry.devilry_examiner.views.assignment.bulkoperations import bulk_add_new_attempt
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group import models as group_models
from devilry.project.common import settings
from devilry.apps.core import models as core_models


class TestBulkAddNewAttempt(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = bulk_add_new_attempt.BulkAddNewAttemptListView

    def setUp(self):
        customsql.AssignmentGroupDbCacheCustomSql().initialize()

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
            requestuser=examiner_user)
        self.assertIn(
            'Bulk add new attempt',
            mockresponse.selector.one('title').alltext_normalized)

    def test_raises_404_with_one_group_corrected(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup,
                   relatedexaminer__user=examiner_user)
        with self.assertRaises(http.Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user)

    def test_raises_404_with_two_group_one_corrected(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=examiner_user)
        with self.assertRaises(http.Http404):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user)

    def test_success_message(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=examiner_user)
        mommy.make('core.Candidate', assignment_group=testgroup1,
                   relatedstudent__user__fullname='Candidate1',
                   relatedstudent__user__shortname='candidate1')
        mommy.make('core.Candidate', assignment_group=testgroup2,
                   relatedstudent__user__fullname='Candidate2',
                   relatedstudent__user__shortname='candidate2')
        # create FeedbackSets for the AssignmentGroups
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        new_deadline = timezone.now() + timezone.timedelta(days=10)
        messagemock = mock.MagicMock()
        self.mock_postrequest(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            requestkwargs={
                'data': {
                    'new_deadline': new_deadline.strftime('%Y-%m-%d %H:%M'),
                    'feedback_comment_text': 'feedback comment',
                    'selected_items': [testgroup1.id]
                }
            },
            messagesmock=messagemock
        )
        messagemock.add.assert_called_once_with(
            messages.SUCCESS,
            'Bulk added new attempt for {}'.format(testgroup1.get_anonymous_displayname(assignment=testassignment)),
            '')

    def test_anonymizationmode_off_canidates(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examineruser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='unanonymizedfullname',
                   relatedstudent__user__fullname='A un-anonymized fullname',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examineruser
        )
        self.assertIn('unanonymizedfullname', mockresponse.response.content)
        self.assertIn('A un-anonymized fullname', mockresponse.response.content)
        self.assertNotIn('MyAnonymousID', mockresponse.response.content)

    def test_anonymizationmode_semi_anonymous_canidates(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examineruser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='unanonymizedfullname',
                   relatedstudent__user__fullname='A un-anonymized fullname',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examineruser
        )
        self.assertNotIn('unanonymizedfullname', mockresponse.response.content)
        self.assertNotIn('A un-anonymized fullname', mockresponse.response.content)
        self.assertIn('MyAnonymousID', mockresponse.response.content)

    def test_anonymizationmode_fully_anonymous_canidates(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        examineruser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='unanonymizedfullname',
                   relatedstudent__user__fullname='A un-anonymized fullname',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examineruser
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
        examineruser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUserA')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                viewkwargs={'filters_string': 'search-TestUser'},
                requestuser=examineruser)
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
        examineruser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='testuser')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                viewkwargs={'filters_string': 'search-testuser'},
                requestuser=examineruser)
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
        examineruser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   candidate_id='MyCandidateID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                viewkwargs={'filters_string': 'search-MyCandidateID'},
                requestuser=examineruser)
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
        examineruser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__candidate_id='MyCandidateID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                viewkwargs={'filters_string': 'search-MyCandidateID'},
                requestuser=examineruser)
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
        examineruser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                viewkwargs={'filters_string': 'search-MyAnonymousID'},
                requestuser=examineruser)
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
        examineruser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUser')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                viewkwargs={'filters_string': 'search-TestUser'},
                requestuser=examineruser)
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
        examineruser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='testuser')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                viewkwargs={'filters_string': 'search-testuser'},
                requestuser=examineruser)
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
        examineruser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__candidate_id='MyCandidateID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                viewkwargs={'filters_string': 'search-MyCandidateID'},
                requestuser=examineruser)
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
        examineruser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                viewkwargs={'filters_string': 'search-MyAnonymousID'},
                requestuser=examineruser)
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
        examineruser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup2)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   candidate_id='MyCandidateID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                viewkwargs={'filters_string': 'search-MyCandidateID'},
                requestuser=examineruser)
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
            requestuser=examiner_user)
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
        new_deadline = timezone.now() + timezone.timedelta(days=10)
        with self.assertRaises(http.Http404):
            self.mock_http302_postrequest(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                requestkwargs={
                    'data': {
                        'feedback_comment_text': 'new attempt given',
                        'new_deadline': new_deadline,
                        'selected_items': [testgroup1.id, testgroup2.id]
                    }
                })

    def test_post_new_feedbackset_deadlines(self):
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
        new_deadline = timezone.now() + timezone.timedelta(days=10)
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            requestkwargs={
                'data': {
                    'feedback_comment_text': 'new attempt given',
                    'new_deadline': new_deadline,
                    'selected_items': [testgroup1.id, testgroup2.id, testgroup3.id]
                }
            })
        feedbacksets = group_models.FeedbackSet.objects.all()
        self.assertEquals(6, feedbacksets.count())
        feedbacksets = feedbacksets.filter(feedbackset_type=group_models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT)
        self.assertEquals(3, feedbacksets.count())
        self.assertIn(new_deadline, [fb.deadline_datetime for fb in feedbacksets])

    def test_post_new_attempt_for_groups(self):
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
        new_deadline = timezone.now() + timezone.timedelta(days=10)
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            requestkwargs={
                'data': {
                    'feedback_comment_text': 'new attempt given',
                    'new_deadline': new_deadline.strftime('%Y-%m-%d %H:%M'),
                    'selected_items': [testgroup1.id, testgroup2.id, testgroup3.id]
                }
            })

        self.assertEquals(6, group_models.FeedbackSet.objects.count())

        cached_data_group1 = cache_models.AssignmentGroupCachedData.objects.get(group_id=testgroup1.id)
        cached_data_group2 = cache_models.AssignmentGroupCachedData.objects.get(group_id=testgroup2.id)
        cached_data_group3 = cache_models.AssignmentGroupCachedData.objects.get(group_id=testgroup3.id)
        self.assertNotEquals(cached_data_group1.last_published_feedbackset, cached_data_group1.last_feedbackset)
        self.assertNotEquals(cached_data_group2.last_published_feedbackset, cached_data_group2.last_feedbackset)
        self.assertNotEquals(cached_data_group3.last_published_feedbackset, cached_data_group3.last_feedbackset)

        group_comments = group_models.GroupComment.objects.all()
        self.assertEquals(3, group_comments.count())
        self.assertIn('new attempt given', [comment.text for comment in group_comments])

    def test_post_new_attempt_added_while_lingering(self):
        # Tests what happens when user lingers in the view and one of the groups get a
        # new attempt in the meantime.
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
        new_deadline = timezone.now() + timezone.timedelta(days=10)

        # group 3 receives a new attempt before post
        devilry_group_mommy_factories.feedbackset_new_attempt_unpublished(group=testgroup3)
        messagemock = mock.MagicMock()
        mockresponse = self.mock_http200_postrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            requestkwargs={
                'data': {
                    'feedback_comment_text': 'new attempt given',
                    'new_deadline': new_deadline.strftime('%Y-%m-%d %H:%M'),
                    'selected_items': [testgroup1.id, testgroup2.id, testgroup3.id]
                }
            },
            messagesmock=messagemock
        )

        self.assertEquals(4, group_models.FeedbackSet.objects.count())
        self.assertEquals(0, group_models.GroupComment.objects.count())

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
                requestuser=examiner_user)

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
        new_deadline = timezone.now() + timezone.timedelta(days=10)

        with self.assertNumQueries(15):
            self.mock_http302_postrequest(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                requestkwargs={
                    'data': {
                        'feedback_comment_text': 'new attempt given',
                        'new_deadline': new_deadline.strftime('%Y-%m-%d %H:%M'),
                        'selected_items': [testgroup1.id, testgroup2.id, testgroup3.id]
                    }
                })
