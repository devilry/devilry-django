# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
from django import test
from django.contrib import messages
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core import models as core_models
from devilry.devilry_dbcache import customsql
from devilry.devilry_dbcache import models as cache_models
from devilry.devilry_examiner.views.assignment.bulkoperations import bulk_feedback
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group import models as group_models
from devilry.project.common import settings


class TestUIPassedFailedBulkCreateView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = bulk_feedback.BulkFeedbackPassedFailedView

    def setUp(self):
        customsql.AssignmentGroupDbCacheCustomSql().initialize()

    def test_title(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup__parentnode=testassignment,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user)
        self.assertIn(
            'Bulk create feedback',
            mockresponse.selector.one('title').alltext_normalized)

    def test_no_groups_where_not_examiner(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup__parentnode=testassignment,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup__parentnode=testassignment,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser
        )
        self.assertEquals(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue')
        )

    def test_groups_sanity_unpublished(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup__parentnode=testassignment,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup__parentnode=testassignment,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user
        )
        self.assertEquals(
            2,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue')
        )

    def test_groups_sanity_published(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        mommy.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user
        )
        self.assertEquals(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue')
        )

    def test_anonymizationmode_off_canidates(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        examineruser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
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
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        examineruser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
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
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        examineruser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
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

    def test_group_render_title_name_order(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='userb')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='usera')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                                          requestuser=testuser)
        self.assertEqual(
            'usera , userb',
            mockresponse.selector.one(
                '.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_group_render_title_name_order_fullname(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='userb')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='userc',
                   relatedstudent__user__fullname='A user')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='usera')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                                          requestuser=testuser)
        self.assertEqual(
            'A user(userc) , usera , userb',
            mockresponse.selector.one(
                '.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_search_nomatch(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testuser')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-nomatch'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_match_fullname(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='TestUser')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-TestUser'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_match_shortname(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testuser')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-testuser'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_nomatch_fullname(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='TestUser')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-TestUser'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_nomatch_shortname(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testuser')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-testuser'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_nomatch_candidate_id_from_candidate(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   candidate_id='MyCandidateID')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-MyCandidateID'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_match_automatic_candidate_id_from_relatedstudent(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__candidate_id='MyCandidateID')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-MyCandidateID'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_match_automatic_anonymous_id(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-MyAnonymousID'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_fullname(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='TestUser')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-TestUser'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_shortname(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testuser')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-testuser'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_automatic_candidate_id_from_relatedstudent(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__candidate_id='MyCandidateID')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-MyCandidateID'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_automatic_anonymous_id(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-MyAnonymousID'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_match_candidate_id_from_candidate(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   candidate_id='MyCandidateID')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-MyCandidateID'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_groups_not_selected_by_default(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user
        )
        self.assertEquals(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-target-with-items'))
        self.assertEquals(
            0,
            mockresponse.selector.count('.django-cradmin-multiselect2-target-selected-item'))

    def test_one_group_on_assignment(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user)
        self.assertEquals(
            1,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_three_groups_on_assignment(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup2)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup3)
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

    def test_examiner_only_examiner_on_one_group(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user)
        self.assertEquals(
            1,
            mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_examiner_group_access_info(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup2)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        candidate1 = mommy.make('core.Candidate',
                                relatedstudent__user__fullname='Donald Duck',
                                relatedstudent__user__shortname='donaldduck',
                                assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__user__fullname='April Duck',
                   relatedstudent__user__shortname='aprilduck',
                   assignment_group=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user
        )
        self.assertEquals(1, mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))
        candidate1_user = candidate1.relatedstudent.user
        self.assertEquals(
            '{}({})'.format(candidate1_user.fullname, candidate1_user.shortname),
            mockresponse.selector.one(
                '.django-cradmin-multiselect2-itemvalue-details:nth-child(1) '
                '.devilry-user-verbose-inline-both').alltext_normalized)

    def test_groups_with_last_published_feedbackset_do_not_show(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user
        )
        self.assertEquals(0, mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))

    def test_filter_search_two_students_one_result(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        candidate = mommy.make('core.Candidate',
                               relatedstudent__user__fullname='Donald Duck',
                               relatedstudent__user__shortname='donaldduck',
                               assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   relatedstudent__user__fullname='April Duck',
                   relatedstudent__user__shortname='aprilduck',
                   assignment_group=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            viewkwargs={'filters_string': 'search-Donald'}
        )
        self.assertEquals(1, mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))
        candidate1_user = candidate.relatedstudent.user
        self.assertEquals(
            '{}({})'.format(candidate1_user.fullname, candidate1_user.shortname),
            mockresponse.selector.one(
                '.django-cradmin-multiselect2-itemvalue-details:nth-child(1) '
                '.devilry-user-verbose-inline-both').alltext_normalized)

    def test_filter_search_three_students_two_results(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1)
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup3,
                   relatedexaminer__user=examiner_user)
        donald_candidate = mommy.make('core.Candidate',
                                relatedstudent__user__fullname='Donald Duck',
                                relatedstudent__user__shortname='donaldduck',
                                assignment_group=testgroup1)
        don_candidate = mommy.make('core.Candidate',
                                relatedstudent__user__fullname='Don Something',
                                relatedstudent__user__shortname='donsomething',
                                assignment_group=testgroup2)
        april_candidate = mommy.make('core.Candidate',
                                     relatedstudent__user__fullname='April Duck',
                                     relatedstudent__user__shortname='aprilduck',
                                     assignment_group=testgroup3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            viewkwargs={'filters_string': 'search-Don'}
        )
        self.assertEquals(2, mockresponse.selector.count('.django-cradmin-multiselect2-itemvalue'))
        element_lst = mockresponse.selector.list('.django-cradmin-multiselect2-itemvalue-details:nth-child(1) '
                                                 '.devilry-user-verbose-inline-both')
        # normalize text to test on it
        element_lst = [e.alltext_normalized for e in element_lst]
        donald_user = donald_candidate.relatedstudent.user
        don_user = don_candidate.relatedstudent.user
        april_user = april_candidate.relatedstudent.user
        self.assertIn(
            '{}({})'.format(donald_user.fullname, donald_user.shortname),
            element_lst
        )
        self.assertIn(
            '{}({})'.format(don_user.fullname, don_user.shortname),
            element_lst
        )
        self.assertNotIn(
            '{}({})'.format(april_user.fullname, april_user.shortname),
            element_lst
        )


class TestPassedFailedBulkCreateFeedback(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = bulk_feedback.BulkFeedbackPassedFailedView

    def setUp(self):
        customsql.AssignmentGroupDbCacheCustomSql().initialize()

    def test_success_message(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        # create assignment group
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)

        # create examiner for group
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)

        mommy.make('core.Candidate', assignment_group=testgroup1,
                   relatedstudent__user__fullname='Candidate',
                   relatedstudent__user__shortname='candidate')

        # create FeedbackSets for the AssignmentGroups
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1)

        messagemock = mock.MagicMock()
        self.mock_postrequest(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            requestkwargs={
                'data': {
                    'passed': True,
                    'feedback_comment_text': 'feedback comment',
                    'selected_items': [testgroup1.id]
                }
            },
            messagesmock=messagemock
        )
        messagemock.add.assert_called_once_with(
            messages.SUCCESS,
            'Bulk added feedback for {}'.format(testgroup1.get_anonymous_displayname(assignment=testassignment)),
            '')

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
            self.assertTrue(group_comment.published_datetime < group_comment.feedback_set.grading_published_datetime)
            self.assertEquals('feedback comment', group_comment.text)

        # Test bulk created FeedbackSets
        feedback_sets = group_models.FeedbackSet.objects.all()
        self.assertEquals(3, feedback_sets.count())
        for feedback_set in feedback_sets:
            self.assertIsNotNone(feedback_set.grading_published_datetime)
            self.assertEquals(feedback_set.grading_points, testassignment.passing_grade_min_points)

    def test_get_num_queries(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        # create AssignmentGroups
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup4 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup5 = mommy.make('core.AssignmentGroup', parentnode=testassignment)

        # create user as examiner for AssignmentGroups
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup4, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup5, relatedexaminer__user=examiner_user)

        # create feedbacksets for the groups
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup1)
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup2)
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup3)
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup4)
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup5)

        with self.assertNumQueries(5):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user
            )

    def test_post_num_queries(self):
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        # create AssignmentGroups
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup4 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup5 = mommy.make('core.AssignmentGroup', parentnode=testassignment)

        # create user as examiner for AssignmentGroups
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup4, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup5, relatedexaminer__user=examiner_user)

        # create feedbacksets for the groups
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup1)
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup2)
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup3)
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup4)
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup5)

        with self.assertNumQueries(17):
            self.mock_postrequest(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                requestkwargs={
                    'data': {
                        'passed': True,
                        'feedback_comment_text': 'feedback comment',
                        'selected_items': [testgroup1.id, testgroup2.id, testgroup3.id, testgroup4.id, testgroup5.id]
                    }
                }
            )


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

    def test_get_num_queries(self):
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
            passing_grade_min_points=6,
            max_points=10)

        # create AssignmentGroups
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup4 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup5 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup6 = mommy.make('core.AssignmentGroup', parentnode=testassignment)

        # create user as examiner for AssignmentGroups
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup4, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup5, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup6, relatedexaminer__user=examiner_user)

        # create feedbacksets for the groups
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup1)
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup2)
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup3)
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup4)
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup5)
        devilry_group_mommy_factories \
            .feedbackset_first_attempt_unpublished(group=testgroup6)

        with self.assertNumQueries(5):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user
            )

    def test_post_num_queries(self):
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
            passing_grade_min_points=6,
            max_points=10)

        # create AssignmentGroups
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup4 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup5 = mommy.make('core.AssignmentGroup', parentnode=testassignment)

        # create user as examiner for AssignmentGroups
        examiner_user = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup4, relatedexaminer__user=examiner_user)
        mommy.make('core.Examiner', assignmentgroup=testgroup5, relatedexaminer__user=examiner_user)

        # create feedbacksets for the groups
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup1)
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup2)
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup3)
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup4)
        devilry_group_mommy_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup5)

        with self.assertNumQueries(17):
            self.mock_postrequest(
                cradmin_role=testassignment,
                requestuser=examiner_user,
                requestkwargs={
                    'data': {
                        'points': 10,
                        'feedback_comment_text': 'feedback comment',
                        'selected_items': [testgroup1.id, testgroup2.id, testgroup3.id, testgroup4.id, testgroup5.id]
                    }
                }
            )
