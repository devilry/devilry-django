# -*- coding: utf-8 -*-


from django.template import defaultfilters
from django.test import override_settings
from django.utils import timezone
from model_bakery import baker
import mock

from django import test
from django.conf import settings

from cradmin_legacy import cradmin_testhelpers

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_baker_factories as group_baker
from devilry.devilry_deadlinemanagement.views import deadline_listview
from devilry.apps.core import models as core_models
from devilry.utils import datetimeutils


@override_settings(DATETIME_FORMAT=datetimeutils.ISODATETIME_DJANGOFORMAT, USE_L10N=False)
class TestExaminerDeadlineListView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = deadline_listview.DeadlineListView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __get_mock_instance(self, assignment):
        mock_instance = mock.MagicMock()
        mock_instance.get_devilryrole_for_requestuser.return_value = 'examiner'
        mock_instance.assignment = assignment
        return mock_instance

    def __get_mock_app(self, user=None):
        mock_app = mock.MagicMock()
        mock_app.get_devilryrole.return_value = 'examiner'
        mock_app.get_accessible_group_queryset.return_value = core_models.AssignmentGroup.objects\
            .filter_examiner_has_access(user=user)
        return mock_app

    def test_pagetitle(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app()
        )
        self.assertEqual('Select deadline to manage', mockresponse.selector.one('title').alltext_normalized)

    def test_heading(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app()
        )
        self.assertEqual('Select deadline',
                          mockresponse.selector.one('h1').alltext_normalized)

    def test_subheading(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app()
        )
        self.assertEqual(
            mockresponse.selector.one('.devilry-deadlinemanagement-select-deadline-subheading').alltext_normalized,
            'Please choose how you would like to manage the deadline.')

    def test_title_with_assignment_first_deadline(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='candidate',
                   relatedstudent__user__fullname='Candidate')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser
        )
        self.assertEqual(
            '{} (Assignment first deadline)'.format(
                defaultfilters.date(testassignment.first_deadline, 'DATETIME_FORMAT')),
            mockresponse.selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_deadline_item_value_group_single_candidate(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='candidate',
                   relatedstudent__user__fullname='Candidate')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser
        )
        self.assertEqual('candidate',
                          mockresponse.selector.one('.devilry-deadlinmanagement-item-value-groups').alltext_normalized)

    def test_deadline_item_value_group_multiple_candidates(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='candidate1',
                   relatedstudent__user__fullname='Candidate1')
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='candidate2',
                   relatedstudent__user__fullname='Candidate2')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser
        )
        self.assertEqual('(candidate1 , candidate2)',
                          mockresponse.selector.one('.devilry-deadlinmanagement-item-value-groups').alltext_normalized)

    def test_deadline_item_value_multiple_groups(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup1)
        group_baker.feedbackset_first_attempt_published(group=testgroup2)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        baker.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='candidate_group1',
                   relatedstudent__user__fullname='Candidate Group 2')
        baker.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__user__shortname='candidate_group2',
                   relatedstudent__user__fullname='Candidate Group 2')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser
        )
        group_value_list = [elem.alltext_normalized for elem in
                            mockresponse.selector.list('.devilry-deadlinmanagement-item-value-groups')]
        self.assertIn('candidate_group1,', group_value_list)
        self.assertIn('candidate_group2', group_value_list)

    def test_deadline_item_value_candidate_semi_anonymous(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='unanonymizedfullname',
                   relatedstudent__user__fullname='A un-anonymized fullname',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser
        )
        self.assertNotContains(mockresponse.response, 'unanonymizedfullname')
        self.assertNotContains(mockresponse.response, 'A un-anonymized fullname')
        self.assertContains(mockresponse.response, 'MyAnonymousID')

    def test_deadline_item_value_candidate_fully_anonymous(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='unanonymizedfullname',
                   relatedstudent__user__fullname='A un-anonymized fullname',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser
        )
        self.assertNotContains(mockresponse.response, 'unanonymizedfullname')
        self.assertNotContains(mockresponse.response, 'A un-anonymized fullname')
        self.assertContains(mockresponse.response, 'MyAnonymousID')

    def test_listed_deadlines(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser
        )
        self.assertTrue(mockresponse.selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription'))
        self.assertEqual(
            '{} (Assignment first deadline)'.format(
                defaultfilters.date(testassignment.first_deadline, 'DATETIME_FORMAT')),
            mockresponse.selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_only_distinct_deadlines_listed(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup1)
        group_baker.feedbackset_first_attempt_published(group=testgroup2)
        group_baker.feedbackset_first_attempt_published(group=testgroup3)
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser
        )
        self.assertTrue(mockresponse.selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription'))
        self.assertEqual(
            '{} (Assignment first deadline)'.format(
                defaultfilters.date(testassignment.first_deadline, 'DATETIME_FORMAT')),
            mockresponse.selector.one(
                '.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_only_distinct_deadlines_listed_multiple(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testuser = baker.make(settings.AUTH_USER_MODEL)

        # Groups with published FeedbackSets using first_deadline
        testgroup_first_deadline1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup_first_deadline2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup_first_deadline1)
        group_baker.feedbackset_first_attempt_published(group=testgroup_first_deadline2)
        baker.make('core.Examiner', assignmentgroup=testgroup_first_deadline1, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup_first_deadline2, relatedexaminer__user=testuser)

        # Groups with published FeedbackSets as new attempt published
        testgroup_new_attempt1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup_new_attempt2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        new_attempt_deadline = timezone.now() - timezone.timedelta(days=1)
        new_attempt_deadline = new_attempt_deadline.replace(microsecond=0)
        group_baker.feedbackset_first_attempt_published(group=testgroup_new_attempt1)
        group_baker.feedbackset_first_attempt_published(group=testgroup_new_attempt2)
        group_baker.feedbackset_new_attempt_published(group=testgroup_new_attempt1,
                                                      deadline_datetime=new_attempt_deadline)
        group_baker.feedbackset_new_attempt_published(group=testgroup_new_attempt2,
                                                      deadline_datetime=new_attempt_deadline)
        baker.make('core.Examiner', assignmentgroup=testgroup_new_attempt1, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup_new_attempt2, relatedexaminer__user=testuser)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser
        )
        self.assertEqual(2, mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue-titledescription'))
        deadline_list = [elem.alltext_normalized for elem in
                         mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual(2, len(deadline_list))
        self.assertIn(
            '{} (Assignment first deadline)'.format(defaultfilters.date(testassignment.first_deadline, 'DATETIME_FORMAT')),
            deadline_list)
        self.assertIn(
            defaultfilters.date(timezone.localtime(new_attempt_deadline), 'DATETIME_FORMAT'),
            deadline_list)

    def test_select_manually_buttons_render_if_more_than_one_group(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup1)
        group_baker.feedbackset_first_attempt_published(group=testgroup2)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-deadlinemanagement-select-groups-buttons'))

    def test_select_manually_buttons_does_not_render_if_less_than_two_groups(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup)
        baker.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser
        )
        self.assertFalse(mockresponse.selector.exists('.devilry-deadlinemanagement-select-groups-buttons'))

    def test_new_attempt_button_rendered_if_more_than_one_group_have_been_corrected(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup1)
        group_baker.feedbackset_first_attempt_published(group=testgroup2)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser
        )
        self.assertTrue(
            mockresponse.selector.exists('#devilry_manage_deadline_{}_new_attempt_all_link'
                                         .format(datetimeutils.datetime_to_url_string(testassignment.first_deadline)))
        )
        self.assertTrue(
            mockresponse.selector.exists('#devilry_manage_deadline_{}_new_attempt_select_link'
                                         .format(datetimeutils.datetime_to_url_string(testassignment.first_deadline)))
        )

    def test_new_attempt_button_not_rendered_if_no_groups_have_been_corrected(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_unpublished(group=testgroup1)
        group_baker.feedbackset_first_attempt_unpublished(group=testgroup2)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser
        )
        self.assertFalse(
            mockresponse.selector.exists('#devilry_manage_deadline_{}_new_attempt_all_link'
                                         .format(datetimeutils.datetime_to_url_string(testassignment.first_deadline)))
        )
        self.assertFalse(
            mockresponse.selector.exists('#devilry_manage_deadline_{}_new_attempt_select_link'
                                         .format(datetimeutils.datetime_to_url_string(testassignment.first_deadline)))
        )

    def test_move_deadline_manually_button_not_rendered_if_group_is_corrected(self):
        """
        Test that move deadline manually should not be rendered if all groups have been corrected.
        """
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup)
        baker.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser
        )
        self.assertFalse(
            mockresponse.selector.exists('.devilry-deadlinemanagement-move-deadline-button-manually-select')
        )

    def test_move_deadline_manually_button_not_rendered_if_all_groups_are_corrected(self):
        """
        Test that move deadline manually should not be rendered if all groups have been corrected.
        """
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup1)
        group_baker.feedbackset_first_attempt_published(group=testgroup2)
        group_baker.feedbackset_first_attempt_published(group=testgroup3)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser
        )
        self.assertFalse(
            mockresponse.selector.exists('.devilry-deadlinemanagement-move-deadline-button-manually-select')
        )

    def test_move_deadline_manually_button_rendered_if_at_least_one_group_is_not_corrected(self):
        """
        If at least one group is corrected, the move deadline manually button should be rendered.
        """
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_unpublished(group=testgroup1)
        group_baker.feedbackset_first_attempt_published(group=testgroup2)
        baker.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_instance=self.__get_mock_instance(testassignment),
            cradmin_role=testassignment,
            cradmin_app=self.__get_mock_app(user=testuser),
            requestuser=testuser
        )
        self.assertTrue(
            mockresponse.selector.count('.devilry-deadlinemanagement-move-deadline-button-manually-select'), 1)

    def test_query_count(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testuser = baker.make(settings.AUTH_USER_MODEL)

        # Groups with published FeedbackSets using first_deadline
        testgroup_first_deadline1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup_first_deadline2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup_first_deadline1)
        group_baker.feedbackset_first_attempt_published(group=testgroup_first_deadline2)
        baker.make('core.Examiner', assignmentgroup=testgroup_first_deadline1, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup_first_deadline2, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup_first_deadline1)
        baker.make('core.Examiner', assignmentgroup=testgroup_first_deadline1)
        baker.make('core.Examiner', assignmentgroup=testgroup_first_deadline2)
        baker.make('core.Examiner', assignmentgroup=testgroup_first_deadline2)
        baker.make('core.Candidate', assignment_group=testgroup_first_deadline1)
        baker.make('core.Candidate', assignment_group=testgroup_first_deadline1)
        baker.make('core.Candidate', assignment_group=testgroup_first_deadline2)
        baker.make('core.Candidate', assignment_group=testgroup_first_deadline2)

        # Groups with published FeedbackSets as new attempt published
        testgroup_new_attempt1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup_new_attempt2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        new_attempt_deadline = timezone.now() - timezone.timedelta(days=1)
        new_attempt_deadline = new_attempt_deadline.replace(microsecond=0)
        group_baker.feedbackset_first_attempt_published(group=testgroup_new_attempt1)
        group_baker.feedbackset_first_attempt_published(group=testgroup_new_attempt2)
        group_baker.feedbackset_new_attempt_published(group=testgroup_new_attempt1,
                                                      deadline_datetime=new_attempt_deadline)
        group_baker.feedbackset_new_attempt_published(group=testgroup_new_attempt2,
                                                      deadline_datetime=new_attempt_deadline)
        baker.make('core.Examiner', assignmentgroup=testgroup_new_attempt1, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup_new_attempt2, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup_new_attempt1)
        baker.make('core.Examiner', assignmentgroup=testgroup_new_attempt1)
        baker.make('core.Examiner', assignmentgroup=testgroup_new_attempt2)
        baker.make('core.Examiner', assignmentgroup=testgroup_new_attempt2)
        baker.make('core.Candidate', assignment_group=testgroup_new_attempt1)
        baker.make('core.Candidate', assignment_group=testgroup_new_attempt1)
        baker.make('core.Candidate', assignment_group=testgroup_new_attempt2)
        baker.make('core.Candidate', assignment_group=testgroup_new_attempt2)

        with self.assertNumQueries(3):
            self.mock_http200_getrequest_htmls(
                cradmin_instance=self.__get_mock_instance(testassignment),
                cradmin_role=testassignment,
                cradmin_app=self.__get_mock_app(user=testuser),
                requestuser=testuser
            )

    def test_anonymous_query_count(self):
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=core_models.Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testuser = baker.make(settings.AUTH_USER_MODEL)

        # Groups with published FeedbackSets using first_deadline
        testgroup_first_deadline1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup_first_deadline2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        group_baker.feedbackset_first_attempt_published(group=testgroup_first_deadline1)
        group_baker.feedbackset_first_attempt_published(group=testgroup_first_deadline2)
        baker.make('core.Examiner', assignmentgroup=testgroup_first_deadline1, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup_first_deadline2, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup_first_deadline1)
        baker.make('core.Examiner', assignmentgroup=testgroup_first_deadline1)
        baker.make('core.Examiner', assignmentgroup=testgroup_first_deadline2)
        baker.make('core.Examiner', assignmentgroup=testgroup_first_deadline2)
        baker.make('core.Candidate', assignment_group=testgroup_first_deadline1)
        baker.make('core.Candidate', assignment_group=testgroup_first_deadline1)
        baker.make('core.Candidate', assignment_group=testgroup_first_deadline2)
        baker.make('core.Candidate', assignment_group=testgroup_first_deadline2)

        # Groups with published FeedbackSets as new attempt published
        testgroup_new_attempt1 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup_new_attempt2 = baker.make('core.AssignmentGroup', parentnode=testassignment)
        new_attempt_deadline = timezone.now() - timezone.timedelta(days=1)
        new_attempt_deadline = new_attempt_deadline.replace(microsecond=0)
        group_baker.feedbackset_first_attempt_published(group=testgroup_new_attempt1)
        group_baker.feedbackset_first_attempt_published(group=testgroup_new_attempt2)
        group_baker.feedbackset_new_attempt_published(group=testgroup_new_attempt1,
                                                      deadline_datetime=new_attempt_deadline)
        group_baker.feedbackset_new_attempt_published(group=testgroup_new_attempt2,
                                                      deadline_datetime=new_attempt_deadline)
        baker.make('core.Examiner', assignmentgroup=testgroup_new_attempt1, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup_new_attempt2, relatedexaminer__user=testuser)
        baker.make('core.Examiner', assignmentgroup=testgroup_new_attempt1)
        baker.make('core.Examiner', assignmentgroup=testgroup_new_attempt1)
        baker.make('core.Examiner', assignmentgroup=testgroup_new_attempt2)
        baker.make('core.Examiner', assignmentgroup=testgroup_new_attempt2)
        baker.make('core.Candidate', assignment_group=testgroup_new_attempt1)
        baker.make('core.Candidate', assignment_group=testgroup_new_attempt1)
        baker.make('core.Candidate', assignment_group=testgroup_new_attempt2)
        baker.make('core.Candidate', assignment_group=testgroup_new_attempt2)

        with self.assertNumQueries(3):
            self.mock_http200_getrequest_htmls(
                cradmin_instance=self.__get_mock_instance(testassignment),
                cradmin_role=testassignment,
                cradmin_app=self.__get_mock_app(user=testuser),
                requestuser=testuser
            )
