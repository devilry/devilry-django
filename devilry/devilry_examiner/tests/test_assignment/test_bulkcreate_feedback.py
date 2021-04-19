# -*- coding: utf-8 -*-


import mock
from django import test
from django.contrib import messages
from django.core import mail
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.apps.core import models as core_models
from devilry.devilry_dbcache import customsql
from devilry.devilry_dbcache import models as cache_models
from devilry.devilry_examiner.views.assignment.bulkoperations import bulk_feedback
from devilry.devilry_group import devilry_group_baker_factories
from devilry.devilry_group import models as group_models
from devilry.devilry_message.models import Message
from devilry.project.common import settings


class TestUIPassedFailedBulkCreateView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = bulk_feedback.BulkFeedbackPassedFailedView

    def setUp(self):
        customsql.AssignmentGroupDbCacheCustomSql().initialize()

    def test_title(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup__parentnode=testassignment,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user)
        self.assertIn(
            'Bulk create feedback',
            mockresponse.selector.one('title').alltext_normalized)

    def test_no_groups_where_not_examiner(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup__parentnode=testassignment,
                   relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup__parentnode=testassignment,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser
        )
        self.assertEqual(
            0,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue')
        )

    def test_groups_sanity_unpublished(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup__parentnode=testassignment,
                   relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup__parentnode=testassignment,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user
        )
        self.assertEqual(
            2,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue')
        )

    def test_groups_sanity_published(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_baker_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_baker_factories.feedbackset_first_attempt_published(group=testgroup2)
        baker.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user
        )
        self.assertEqual(
            0,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue')
        )

    def test_anonymizationmode_off_canidates(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_OFF)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        examineruser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='unanonymizedfullname',
                   relatedstudent__user__fullname='A un-anonymized fullname',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examineruser
        )
        self.assertContains(mockresponse.response, 'unanonymizedfullname')
        self.assertContains(mockresponse.response, 'A un-anonymized fullname')
        self.assertNotContains(mockresponse.response, 'MyAnonymousID')

    def test_anonymizationmode_semi_anonymous_canidates(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        examineruser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='unanonymizedfullname',
                   relatedstudent__user__fullname='A un-anonymized fullname',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examineruser
        )
        self.assertNotContains(mockresponse.response, 'unanonymizedfullname')
        self.assertNotContains(mockresponse.response, 'A un-anonymized fullname')
        self.assertContains(mockresponse.response, 'MyAnonymousID')

    def test_anonymizationmode_fully_anonymous_canidates(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        examineruser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner',
                   relatedexaminer__user=examineruser,
                   assignmentgroup=testgroup)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='unanonymizedfullname',
                   relatedstudent__user__fullname='A un-anonymized fullname',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examineruser
        )
        self.assertNotContains(mockresponse.response, 'unanonymizedfullname')
        self.assertNotContains(mockresponse.response, 'A un-anonymized fullname')
        self.assertContains(mockresponse.response, 'MyAnonymousID')

    def test_group_render_title_name_order(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Examiner', relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='userb')
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='usera')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                                          requestuser=testuser)
        self.assertEqual(
            'usera , userb',
            mockresponse.selector.one(
                '.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_group_render_title_name_order_fullname(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Examiner', relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='userb')
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='userc',
                   relatedstudent__user__fullname='A user')
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='usera')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                                          requestuser=testuser)
        self.assertEqual(
            'A user(userc) , usera , userb',
            mockresponse.selector.one(
                '.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_search_nomatch(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testuser')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-nomatch'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))

    def test_search_match_fullname(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='TestUser')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-TestUser'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))

    def test_search_match_shortname(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testuser')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-testuser'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))

    def test_search_anonymous_nomatch_fullname(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='TestUser')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-TestUser'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))

    def test_search_anonymous_nomatch_shortname(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testuser')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-testuser'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))

    def test_search_anonymous_nomatch_candidate_id_from_candidate(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   candidate_id='MyCandidateID')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-MyCandidateID'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))

    def test_search_anonymous_match_automatic_candidate_id_from_relatedstudent(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__candidate_id='MyCandidateID')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-MyCandidateID'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))

    def test_search_anonymous_match_automatic_anonymous_id(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-MyAnonymousID'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_fullname(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='TestUser')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-TestUser'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_shortname(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testuser')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-testuser'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_automatic_candidate_id_from_relatedstudent(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__candidate_id='MyCandidateID')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-MyCandidateID'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_automatic_anonymous_id(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='TestUser',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-MyAnonymousID'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_match_candidate_id_from_candidate(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   candidate_id='MyCandidateID')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                viewkwargs={'filters_string': 'search-MyCandidateID'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))

    def test_groups_not_selected_by_default(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user
        )
        self.assertEqual(
            0,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-target-with-items'))
        self.assertEqual(
            0,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-target-selected-item'))

    def test_one_group_on_assignment(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))

    def test_three_groups_on_assignment(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup1)
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup2)
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup3)
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup3,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user)
        self.assertEqual(
            3,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))

    def test_examiner_only_examiner_on_one_group(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup1)
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup2)
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))

    def test_examiner_group_access_info(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup1)
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup2)
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner',
                   assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        candidate1 = baker.make('core.Candidate',
                                relatedstudent__user__fullname='Donald Duck',
                                relatedstudent__user__shortname='donaldduck',
                                assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__user__fullname='April Duck',
                   relatedstudent__user__shortname='aprilduck',
                   assignment_group=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user
        )
        self.assertEqual(1, mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))
        candidate1_user = candidate1.relatedstudent.user
        self.assertEqual(
            '{}({})'.format(candidate1_user.fullname, candidate1_user.shortname),
            mockresponse.selector.one(
                '.cradmin-legacy-multiselect2-itemvalue-details:nth-child(1) '
                '.devilry-user-verbose-inline-both').alltext_normalized)

    def test_groups_with_last_published_feedbackset_do_not_show(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_baker_factories.feedbackset_first_attempt_published(group=testgroup)
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup,
                   relatedexaminer__user=examiner_user)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user
        )
        self.assertEqual(0, mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))

    def test_filter_search_two_students_one_result(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup1)
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner',
                   assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        baker.make('core.Examiner',
                   assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        candidate = baker.make('core.Candidate',
                               relatedstudent__user__fullname='Donald Duck',
                               relatedstudent__user__shortname='donaldduck',
                               assignment_group=testgroup1)
        baker.make('core.Candidate',
                   relatedstudent__user__fullname='April Duck',
                   relatedstudent__user__shortname='aprilduck',
                   assignment_group=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            viewkwargs={'filters_string': 'search-Donald'}
        )
        self.assertEqual(1, mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))
        candidate1_user = candidate.relatedstudent.user
        self.assertEqual(
            '{}({})'.format(candidate1_user.fullname, candidate1_user.shortname),
            mockresponse.selector.one(
                '.cradmin-legacy-multiselect2-itemvalue-details:nth-child(1) '
                '.devilry-user-verbose-inline-both').alltext_normalized)

    def test_filter_search_three_students_two_results(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment 0')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup1)
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner',
                   assignmentgroup=testgroup1,
                   relatedexaminer__user=examiner_user)
        baker.make('core.Examiner',
                   assignmentgroup=testgroup2,
                   relatedexaminer__user=examiner_user)
        baker.make('core.Examiner',
                   assignmentgroup=testgroup3,
                   relatedexaminer__user=examiner_user)
        donald_candidate = baker.make('core.Candidate',
                                relatedstudent__user__fullname='Donald Duck',
                                relatedstudent__user__shortname='donaldduck',
                                assignment_group=testgroup1)
        don_candidate = baker.make('core.Candidate',
                                relatedstudent__user__fullname='Don Something',
                                relatedstudent__user__shortname='donsomething',
                                assignment_group=testgroup2)
        april_candidate = baker.make('core.Candidate',
                                     relatedstudent__user__fullname='April Duck',
                                     relatedstudent__user__shortname='aprilduck',
                                     assignment_group=testgroup3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=examiner_user,
            viewkwargs={'filters_string': 'search-Don'}
        )
        self.assertEqual(2, mockresponse.selector.count('.cradmin-legacy-multiselect2-itemvalue'))
        element_lst = mockresponse.selector.list('.cradmin-legacy-multiselect2-itemvalue-details:nth-child(1) '
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
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        # create assignment group
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # create examiner for group
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)

        baker.make('core.Candidate', assignment_group=testgroup1,
                   relatedstudent__user__fullname='Candidate',
                   relatedstudent__user__shortname='candidate')

        # create FeedbackSets for the AssignmentGroups
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup1)

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
            'Bulk added feedback for {}'.format(testgroup1.short_displayname),
            '')

    def test_success_message_assignment_is_anonymous(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)

        # create assignment group
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # create examiner for group
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)

        baker.make('core.Candidate', assignment_group=testgroup1,
                   relatedstudent__user__fullname='Candidate',
                   relatedstudent__user__shortname='candidate')

        # create FeedbackSets for the AssignmentGroups
        devilry_group_baker_factories.feedbackset_first_attempt_unpublished(group=testgroup1)

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
            'Bulk added feedback for Automatic anonymous ID missing'.format(testgroup1.short_displayname),
            '')

    def test_only_bulk_create_passed_group_ids(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        # create assignment group
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # create examiner for group
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)

        # create FeedbackSets for the AssignmentGroups
        testfeedbackset_first_attempt = devilry_group_baker_factories\
            .feedbackset_first_attempt_published(group=testgroup1)
        testfeedbackset_new_attempt = devilry_group_baker_factories\
            .feedbackset_new_attempt_unpublished(group=testgroup1)
        devilry_group_baker_factories \
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
        self.assertNotEqual(testfeedbackset_first_attempt, cached_data_group1.last_published_feedbackset)
        self.assertEqual(testfeedbackset_new_attempt, cached_data_group1.last_published_feedbackset)
        self.assertEqual(1, group_models.GroupComment.objects.count())

        cached_data_group2 = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup2)
        self.assertIsNone(cached_data_group2.last_published_feedbackset)

    def test_group_receives_bulk_feedback(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        # create assignment group
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # create examiner for group
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=examiner_user)

        # create feedbacksets for the groups
        testfeedbackset_first_attempt = devilry_group_baker_factories\
            .feedbackset_first_attempt_published(group=testgroup)
        testfeedbackset_new_attempt = devilry_group_baker_factories\
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
        self.assertNotEqual(testfeedbackset_first_attempt, cached_data.last_published_feedbackset)
        self.assertEqual(testfeedbackset_new_attempt, cached_data.last_published_feedbackset)
        self.assertEqual(1, group_models.GroupComment.objects.count())
        comment = group_models.GroupComment.objects.all()[0]
        self.assertEqual('feedback comment', comment.text)
        self.assertEqual(testassignment.passing_grade_min_points,
                          cached_data.last_published_feedbackset.grading_points)

    def test_multiple_groups_receive_bulk_feedback(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        # create AssignmentGroups
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # create students for the groups
        student1 = baker.make('core.Candidate', assignment_group=testgroup1)
        student2 = baker.make('core.Candidate', assignment_group=testgroup2)
        student3 = baker.make('core.Candidate', assignment_group=testgroup3)
        baker.make('devilry_account.UserEmail', user=student1.relatedstudent.user, email='student1@example.com')
        baker.make('devilry_account.UserEmail', user=student2.relatedstudent.user, email='student2@example.com')
        baker.make('devilry_account.UserEmail', user=student3.relatedstudent.user, email='student3@example.com')

        # create user as examiner for AssignmentGroups
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=examiner_user)

        # create feedbacksets for the groups
        testfeedbackset_group1 = devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup1)
        testfeedbackset_group2 = devilry_group_baker_factories \
            .feedbackset_first_attempt_unpublished(group=testgroup2)
        testfeedbackset_group3 = devilry_group_baker_factories \
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
        self.assertEqual(testfeedbackset_group1, cached_data_group1.last_published_feedbackset)
        self.assertEqual(testfeedbackset_group2, cached_data_group2.last_published_feedbackset)
        self.assertEqual(testfeedbackset_group3, cached_data_group3.last_published_feedbackset)

        # Test bulk created GroupComments
        group_comments = group_models.GroupComment.objects.all()
        self.assertEqual(3, group_comments.count())
        for group_comment in group_comments:
            self.assertTrue(group_comment.published_datetime < group_comment.feedback_set.grading_published_datetime)
            self.assertEqual('feedback comment', group_comment.text)

        # Test bulk created FeedbackSets
        feedback_sets = group_models.FeedbackSet.objects.all()
        self.assertEqual(3, feedback_sets.count())
        for feedback_set in feedback_sets:
            self.assertIsNotNone(feedback_set.grading_published_datetime)
            self.assertEqual(feedback_set.grading_points, testassignment.passing_grade_min_points)
        self.assertEqual(len(mail.outbox), 3)

    def test_get_num_queries(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        # create AssignmentGroups
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup4 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup5 = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # create user as examiner for AssignmentGroups
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup4, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup5, relatedexaminer__user=examiner_user)

        # create feedbacksets for the groups
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup1)
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup2)
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup3)
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup4)
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup5)

        with self.assertNumQueries(5):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user
            )

    def test_post_num_queries(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        # create AssignmentGroups
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup4 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup5 = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # create user as examiner for AssignmentGroups
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup4, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup5, relatedexaminer__user=examiner_user)

        # create feedbacksets for the groups
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup1)
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup2)
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup3)
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup4)
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup5)

        with self.assertNumQueries(22):
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
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
            passing_grade_min_points=6,
            max_points=10)

        # create assignment group
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # create examiner for group
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)

        # create FeedbackSets for the AssignmentGroups
        testfeedbackset_first_attempt = devilry_group_baker_factories\
            .feedbackset_first_attempt_published(group=testgroup1)
        testfeedbackset_new_attempt = devilry_group_baker_factories\
            .feedbackset_new_attempt_unpublished(group=testgroup1)
        devilry_group_baker_factories \
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
        self.assertNotEqual(testfeedbackset_first_attempt, cached_data_group1.last_published_feedbackset)
        self.assertEqual(testfeedbackset_new_attempt, cached_data_group1.last_published_feedbackset)
        self.assertEqual(1, group_models.GroupComment.objects.count())

        cached_data_group2 = cache_models.AssignmentGroupCachedData.objects.get(group=testgroup2)
        self.assertIsNone(cached_data_group2.last_published_feedbackset)

    def test_group_receives_bulk_feedback(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
            passing_grade_min_points=6,
            max_points=10)

        # create assignment group
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # create examiner for group
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=examiner_user)

        # create feedbacksets for the groups
        testfeedbackset_first_attempt = devilry_group_baker_factories\
            .feedbackset_first_attempt_published(group=testgroup)
        testfeedbackset_new_attempt = devilry_group_baker_factories\
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
        self.assertNotEqual(testfeedbackset_first_attempt, cached_data.last_published_feedbackset)
        self.assertEqual(testfeedbackset_new_attempt, cached_data.last_published_feedbackset)
        self.assertEqual(1, group_models.GroupComment.objects.count())
        comment = group_models.GroupComment.objects.all()[0]
        self.assertEqual('feedback comment', comment.text)
        self.assertEqual(10, cached_data.last_published_feedbackset.grading_points)

    def test_multiple_groups_receive_bulk_feedback(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
            passing_grade_min_points=6,
            max_points=10)

        # create AssignmentGroups
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # create students for the groups
        student1 = baker.make('core.Candidate', assignment_group=testgroup1)
        student2 = baker.make('core.Candidate', assignment_group=testgroup2)
        student3 = baker.make('core.Candidate', assignment_group=testgroup3)
        baker.make('devilry_account.UserEmail', user=student1.relatedstudent.user, email='student1@example.com')
        baker.make('devilry_account.UserEmail', user=student2.relatedstudent.user, email='student2@example.com')
        baker.make('devilry_account.UserEmail', user=student3.relatedstudent.user, email='student3@example.com')

        # create user as examiner for AssignmentGroups
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=examiner_user)

        # create feedbacksets for the groups
        testfeedbackset_group1 = devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup1)
        testfeedbackset_group2 = devilry_group_baker_factories \
            .feedbackset_first_attempt_unpublished(group=testgroup2)
        testfeedbackset_group3 = devilry_group_baker_factories \
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
        self.assertEqual(testfeedbackset_group1, cached_data_group1.last_published_feedbackset)
        self.assertEqual(testfeedbackset_group2, cached_data_group2.last_published_feedbackset)
        self.assertEqual(testfeedbackset_group3, cached_data_group3.last_published_feedbackset)

        # Test bulk created GroupComments
        group_comments = group_models.GroupComment.objects.all()
        self.assertEqual(3, group_comments.count())
        for group_comment in group_comments:
            self.assertEqual('feedback comment', group_comment.text)

        # Test bulk created FeedbackSets
        feedback_sets = group_models.FeedbackSet.objects.all()
        self.assertEqual(3, feedback_sets.count())
        for feedback_set in feedback_sets:
            self.assertIsNotNone(feedback_set.grading_published_datetime)
            self.assertEqual(10, feedback_set.grading_points)
        self.assertEqual(len(mail.outbox), 3)

    def test_get_num_queries(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
            passing_grade_min_points=6,
            max_points=10)

        # create AssignmentGroups
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup4 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup5 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup6 = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # create students for the groups
        student1 = baker.make('core.Candidate', assignment_group=testgroup1)
        student2 = baker.make('core.Candidate', assignment_group=testgroup2)
        student3 = baker.make('core.Candidate', assignment_group=testgroup3)
        student4 = baker.make('core.Candidate', assignment_group=testgroup4)
        student5 = baker.make('core.Candidate', assignment_group=testgroup5)
        student6 = baker.make('core.Candidate', assignment_group=testgroup6)
        baker.make('devilry_account.UserEmail', user=student1.relatedstudent.user, email='student1@example.com')
        baker.make('devilry_account.UserEmail', user=student2.relatedstudent.user, email='student2@example.com')
        baker.make('devilry_account.UserEmail', user=student3.relatedstudent.user, email='student3@example.com')
        baker.make('devilry_account.UserEmail', user=student4.relatedstudent.user, email='student4@example.com')
        baker.make('devilry_account.UserEmail', user=student5.relatedstudent.user, email='student5@example.com')
        baker.make('devilry_account.UserEmail', user=student6.relatedstudent.user, email='student6@example.com')

        # create user as examiner for AssignmentGroups
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup4, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup5, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup6, relatedexaminer__user=examiner_user)

        # create feedbacksets for the groups
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup1)
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup2)
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup3)
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup4)
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup5)
        devilry_group_baker_factories \
            .feedbackset_first_attempt_unpublished(group=testgroup6)

        with self.assertNumQueries(10):
            self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=examiner_user
            )

    def test_post_num_queries(self):
        testassignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            grading_system_plugin_id=core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
            passing_grade_min_points=6,
            max_points=10)

        # create AssignmentGroups
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup4 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup5 = baker.make('core.AssignmentGroup', parentnode=testassignment)

        # create students for the groups
        student1 = baker.make('core.Candidate', assignment_group=testgroup1)
        student2 = baker.make('core.Candidate', assignment_group=testgroup2)
        student3 = baker.make('core.Candidate', assignment_group=testgroup3)
        student4 = baker.make('core.Candidate', assignment_group=testgroup4)
        student5 = baker.make('core.Candidate', assignment_group=testgroup5)
        baker.make('devilry_account.UserEmail', user=student1.relatedstudent.user, email='student1@example.com')
        baker.make('devilry_account.UserEmail', user=student2.relatedstudent.user, email='student2@example.com')
        baker.make('devilry_account.UserEmail', user=student3.relatedstudent.user, email='student3@example.com')
        baker.make('devilry_account.UserEmail', user=student4.relatedstudent.user, email='student4@example.com')
        baker.make('devilry_account.UserEmail', user=student5.relatedstudent.user, email='student5@example.com')

        # create user as examiner for AssignmentGroups
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup4, relatedexaminer__user=examiner_user)
        baker.make('core.Examiner', assignmentgroup=testgroup5, relatedexaminer__user=examiner_user)

        # create feedbacksets for the groups
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup1)
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup2)
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup3)
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup4)
        devilry_group_baker_factories\
            .feedbackset_first_attempt_unpublished(group=testgroup5)

        with self.assertNumQueries(93):
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
