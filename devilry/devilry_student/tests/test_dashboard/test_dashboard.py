

from datetime import timedelta, datetime

import htmls
import mock
from django import test
from django.conf import settings
from django.utils import timezone
from cradmin_legacy import cradmin_testhelpers
from cradmin_legacy import crapp
from cradmin_legacy.crinstance import reverse_cradmin_url
from model_bakery import baker

from devilry.apps.core.models import Assignment
from devilry.apps.core.baker_recipes import ACTIVE_PERIOD_START, ACTIVE_PERIOD_END
from devilry.devilry_comment.models import Comment
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_baker_factories
from devilry.devilry_group.models import GroupComment
from devilry.devilry_student.views.dashboard import dashboard


class TestDashboardView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = dashboard.DashboardView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_title(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate', relatedstudent__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertIn(
                'Student dashboard',
                mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate', relatedstudent__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                'Student dashboard',
                mockresponse.selector.one('h1').alltext_normalized)

    def test_page_subheader(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate', relatedstudent__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                'Welcome! Please select an assignment below to add deliveries, '
                'view feedback or communicate with you examiner.',
                mockresponse.selector.one('.devilry-page-subheader').alltext_normalized)

    def __make_candidate_and_group_for_assignment(self, assignment, user, deadline_datetime):
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        baker.make('devilry_group.FeedbackSet', group=group, deadline_datetime=deadline_datetime)
        baker.make('core.Candidate', relatedstudent__user=user, assignment_group=group)

    def test_upcoming_assignments_header(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
            mockresponse.selector.one('.devilry-student-dashboard-upcoming-assignments-header').alltext_normalized,
            'Upcoming assignments')

    def test_upcoming_assignments_no_assignments_text(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
            mockresponse.selector.one('.devilry-student-dashboard-no-upcoming-assignments-text').alltext_normalized,
            'You have no upcoming assignments with deadlines within the next 7 days.')

    def test_upcoming_assignments_text(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        self.__make_candidate_and_group_for_assignment(
            assignment=testassignment, user=testuser, deadline_datetime=timezone.now() + timezone.timedelta(days=1))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
            mockresponse.selector.one('.devilry-student-dashboard-upcoming-assignments-text').alltext_normalized,
            'Upcoming assignments with deadlines within the next 7 days.')

    def test_upcoming_assignments_past_assignment_not_rendered(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        self.__make_candidate_and_group_for_assignment(
            assignment=testassignment, user=testuser, deadline_datetime=timezone.now() - timezone.timedelta(days=1))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        selector = htmls.S(mockresponse.selector.one('.devilry-student-dashboard-upcoming-assignments').__str__())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue'))

    def test_upcoming_assignments_over_seven_days_to_deadline_not_rendered(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        self.__make_candidate_and_group_for_assignment(
            assignment=testassignment, user=testuser, deadline_datetime=timezone.now() + timezone.timedelta(days=8))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        selector = htmls.S(mockresponse.selector.one('.devilry-student-dashboard-upcoming-assignments').__str__())
        self.assertFalse(selector.exists('.devilry-cradmin-groupitemvalue'))

    def test_one_upcoming_assignment(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testsubject = baker.make('core.Subject', short_name='testsubject')
        testperiod = baker.make_recipe('devilry.apps.core.period_active',
                                       short_name='testperiod', parentnode=testsubject)
        testassignment1 = baker.make('core.Assignment', parentnode=testperiod,
                                     long_name='Test Assignment 1')
        testassignment2 = baker.make('core.Assignment', parentnode=testperiod,
                                     long_name='Test Assignment 2')
        self.__make_candidate_and_group_for_assignment(
            assignment=testassignment1, user=testuser, deadline_datetime=timezone.now() + timezone.timedelta(days=1))
        self.__make_candidate_and_group_for_assignment(
            assignment=testassignment2, user=testuser, deadline_datetime=timezone.now() + timezone.timedelta(days=8))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        selector = htmls.S(mockresponse.selector.one('.devilry-student-dashboard-upcoming-assignments').__str__())
        self.assertEqual(
            selector.one('.devilry-cradmin-groupitemvalue '
                         '.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized,
            'testsubject.testperiod - Test Assignment 1')

    def test_one_upcoming_assignments_accross_periods(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testsubject = baker.make('core.Subject', short_name='testsubject')
        testperiod1 = baker.make_recipe('devilry.apps.core.period_active',
                                        short_name='testperiod1', parentnode=testsubject)
        testperiod2 = baker.make_recipe('devilry.apps.core.period_active',
                                        short_name='testperiod2', parentnode=testsubject)
        testassignment1 = baker.make('core.Assignment', parentnode=testperiod1,
                                     long_name='Test Assignment 1')
        testassignment2 = baker.make('core.Assignment', parentnode=testperiod2,
                                     long_name='Test Assignment 2')
        self.__make_candidate_and_group_for_assignment(
            assignment=testassignment1, user=testuser, deadline_datetime=timezone.now() + timezone.timedelta(days=1))
        self.__make_candidate_and_group_for_assignment(
            assignment=testassignment2, user=testuser, deadline_datetime=timezone.now() + timezone.timedelta(days=4))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        selector = htmls.S(mockresponse.selector.one('.devilry-student-dashboard-upcoming-assignments').__str__())
        assignment_name_list = [element.alltext_normalized for element in
                                selector.list('.devilry-cradmin-groupitemvalue '
                                              '.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual(assignment_name_list[0], 'testsubject.testperiod1 - Test Assignment 1')
        self.assertEqual(assignment_name_list[1], 'testsubject.testperiod2 - Test Assignment 2')

    def test_one_upcoming_assignments_accross_subject(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testsubject1 = baker.make('core.Subject', short_name='testsubject1')
        testsubject2 = baker.make('core.Subject', short_name='testsubject2')
        testperiod1 = baker.make_recipe('devilry.apps.core.period_active',
                                        short_name='testperiod1', parentnode=testsubject1)
        testperiod2 = baker.make_recipe('devilry.apps.core.period_active',
                                        short_name='testperiod2', parentnode=testsubject2)
        testassignment1 = baker.make('core.Assignment', parentnode=testperiod1,
                                     long_name='Test Assignment 1')
        testassignment2 = baker.make('core.Assignment', parentnode=testperiod2,
                                     long_name='Test Assignment 2')
        self.__make_candidate_and_group_for_assignment(
            assignment=testassignment1, user=testuser, deadline_datetime=timezone.now() + timezone.timedelta(days=1))
        self.__make_candidate_and_group_for_assignment(
            assignment=testassignment2, user=testuser, deadline_datetime=timezone.now() + timezone.timedelta(days=4))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        selector = htmls.S(mockresponse.selector.one('.devilry-student-dashboard-upcoming-assignments').__str__())
        assignment_name_list = [element.alltext_normalized for element in
                                selector.list('.devilry-cradmin-groupitemvalue '
                                              '.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual(assignment_name_list[0], 'testsubject1.testperiod1 - Test Assignment 1')
        self.assertEqual(assignment_name_list[1], 'testsubject2.testperiod2 - Test Assignment 2')

    def test_multiple_upcoming_assignment(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testsubject = baker.make('core.Subject', short_name='testsubject')
        testperiod = baker.make_recipe('devilry.apps.core.period_active',
                                       short_name='testperiod', parentnode=testsubject)
        testassignment1 = baker.make('core.Assignment', parentnode=testperiod,
                                     long_name='Test Assignment 1')
        testassignment2 = baker.make('core.Assignment', parentnode=testperiod,
                                     long_name='Test Assignment 2')
        testassignment3 = baker.make('core.Assignment', parentnode=testperiod,
                                     long_name='Test Assignment 3')
        self.__make_candidate_and_group_for_assignment(
            assignment=testassignment1, user=testuser, deadline_datetime=timezone.now() + timezone.timedelta(days=1))
        self.__make_candidate_and_group_for_assignment(
            assignment=testassignment2, user=testuser, deadline_datetime=timezone.now() + timezone.timedelta(days=3))
        self.__make_candidate_and_group_for_assignment(
            assignment=testassignment3, user=testuser, deadline_datetime=timezone.now() + timezone.timedelta(days=5))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        selector = htmls.S(mockresponse.selector.one('.devilry-student-dashboard-upcoming-assignments').__str__())
        assignment_name_list = [element.alltext_normalized for element in
                                selector.list('.devilry-cradmin-groupitemvalue '
                                              '.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]
        self.assertEqual(assignment_name_list[0], 'testsubject.testperiod - Test Assignment 1')
        self.assertEqual(assignment_name_list[1], 'testsubject.testperiod - Test Assignment 2')
        self.assertEqual(assignment_name_list[2], 'testsubject.testperiod - Test Assignment 3')

    def test_user_can_not_see_upcoming_assignments_for_other_students_on_same_assignment(self):
        testuser1 = baker.make(settings.AUTH_USER_MODEL)
        testuser2 = baker.make(settings.AUTH_USER_MODEL)
        testsubject = baker.make('core.Subject', short_name='testsubject')
        testperiod = baker.make_recipe('devilry.apps.core.period_active',
                                       short_name='testperiod', parentnode=testsubject)
        testassignment = baker.make('core.Assignment', parentnode=testperiod,
                                     long_name='Test Assignment 1')
        self.__make_candidate_and_group_for_assignment(
            assignment=testassignment, user=testuser1, deadline_datetime=timezone.now() + timezone.timedelta(days=1))
        self.__make_candidate_and_group_for_assignment(
            assignment=testassignment, user=testuser2, deadline_datetime=timezone.now() + timezone.timedelta(days=3))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser1)
        selector = htmls.S(mockresponse.selector.one('.devilry-student-dashboard-upcoming-assignments').__str__())
        self.assertEqual(
            selector.one(
                '.devilry-cradmin-groupitemvalue '
                '.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized,
            'testsubject.testperiod - Test Assignment 1')

    def test_user_can_not_see_upcoming_assignments_for_other_students_on_different_assignments(self):
        testuser1 = baker.make(settings.AUTH_USER_MODEL)
        testuser2 = baker.make(settings.AUTH_USER_MODEL)
        testsubject = baker.make('core.Subject', short_name='testsubject')
        testperiod = baker.make_recipe('devilry.apps.core.period_active',
                                       short_name='testperiod', parentnode=testsubject)
        testassignment1 = baker.make('core.Assignment', parentnode=testperiod,
                                     long_name='Test Assignment 1')
        testassignment2 = baker.make('core.Assignment', parentnode=testperiod,
                                     long_name='Test Assignment 2')
        self.__make_candidate_and_group_for_assignment(
            assignment=testassignment1, user=testuser1, deadline_datetime=timezone.now() + timezone.timedelta(days=1))
        self.__make_candidate_and_group_for_assignment(
            assignment=testassignment2, user=testuser2, deadline_datetime=timezone.now() + timezone.timedelta(days=3))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser1)
        selector = htmls.S(mockresponse.selector.one('.devilry-student-dashboard-upcoming-assignments').__str__())
        self.assertEqual(
            selector.one(
                '.devilry-cradmin-groupitemvalue '
                '.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized,
            'testsubject.testperiod - Test Assignment 1')

    def __get_assignment_count(self, selector):
        return selector.count('.devilry-cradmin-groupitemvalue')

    def test_not_assignments_where_not_student(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                0,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_not_future_periods(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe('devilry.apps.core.assignment_futureperiod_start'))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                0,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_not_old_periods(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe('devilry.apps.core.assignment_oldperiod_end'))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                0,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_include_active_periods(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate', relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_no_active_assignments_message(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                'You have no active assignments. Use the button below to browse '
                'inactive assignments and courses.',
                mockresponse.selector.one('.cradmin-legacy-listing-no-items-message').alltext_normalized)

    def test_assignment_url(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testcandidate = baker.make('core.Candidate', relatedstudent__user=testuser,
                                   assignment_group__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                reverse_cradmin_url(
                        instanceid='devilry_group_student',
                        appname='feedbackfeed',
                        roleid=testcandidate.assignment_group_id,
                        viewname=crapp.INDEXVIEW_NAME,
                ),
                mockresponse.selector.one('a.devilry-student-listbuilder-grouplist-itemframe')['href'])

    def test_grouplist_search_nomatch(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start'))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-nomatch'},
                requestuser=testuser)
        self.assertEqual(
                0,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_subject_short_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode__parentnode__short_name='testsubject'))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-testsubject'},
                requestuser=testuser)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_subject_long_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode__parentnode__long_name='Testsubject'))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-Testsubject'},
                requestuser=testuser)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_period_short_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode__short_name='testperiod'))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-testperiod'},
                requestuser=testuser)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_period_long_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode__long_name='Testperiod'))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-Testperiod'},
                requestuser=testuser)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_assignment_short_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           short_name='testassignment'))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-testassignment'},
                requestuser=testuser)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_assignment_long_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           long_name='Testassignment'))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-Testassignment'},
                requestuser=testuser)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def __get_assignment_titles(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.devilry-cradmin-groupitemvalue '
                                             '.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]

    def test_grouplist_orderby(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod1 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject1',
                                        short_name='testperiod')
        testperiod2 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject2',
                                        short_name='testperiod')
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           long_name='Assignment 1',
                           first_deadline=ACTIVE_PERIOD_START + timedelta(days=1),
                           parentnode=testperiod1))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           long_name='Assignment 2',
                           first_deadline=ACTIVE_PERIOD_START + timedelta(days=3),
                           parentnode=testperiod1))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           long_name='Assignment 1',
                           first_deadline=ACTIVE_PERIOD_START + timedelta(days=2),
                           parentnode=testperiod2))
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser)
        self.assertEqual(
                [
                    'testsubject1.testperiod - Assignment 2',
                    'testsubject2.testperiod - Assignment 1',
                    'testsubject1.testperiod - Assignment 1',
                ],
                self.__get_assignment_titles(mockresponse.selector))

    def test_grouplist_title_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe(
                                       'devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__parentnode__short_name='testsubject',
                                       parentnode__short_name='testperiod',
                                       long_name='Test Assignment'))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser)
        self.assertEqual(
            'testsubject.testperiod - Test Assignment',
            mockresponse.selector.one(
                    '.devilry-cradmin-groupitemvalue '
                    '.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized
        )

    def test_grouplist_no_examiners(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        baker.make('core.Examiner',
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser)
        self.assertTrue(
            mockresponse.selector.exists('.devilry-cradmin-groupitemvalue'))
        self.assertFalse(
            mockresponse.selector.exists('.devilry-cradmin-groupitemvalue-examiners'))

    def test_grouplist_deadline_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make(
            'core.AssignmentGroup',
            parentnode=baker.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                first_deadline=datetime(2000, 1, 15, 12, 0)))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        with self.settings(DATETIME_FORMAT='Y-m-d H:i', USE_L10N=False):
            mockresponse = self.mock_http200_getrequest_htmls(
                    requestuser=testuser)
        self.assertEqual(
            '2000-01-15 12:00',
            mockresponse.selector.one(
                    '.devilry-cradmin-groupitemvalue-deadline__datetime').alltext_normalized
        )

    def test_grouplist_status_waiting_for_deliveries_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=3)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=timezone.now() + timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser)
        selector = htmls.S(mockresponse.selector.one('.devilry-student-dashboard-all-assignments').__str__())
        self.assertFalse(
                selector.exists(
                        '.devilry-cradmin-groupitemvalue '
                        '.devilry-cradmin-groupitemvalue-grade'))
        self.assertEqual(
                'Status: waiting for deliveries',
                selector.one(
                        '.devilry-cradmin-groupitemvalue '
                        '.devilry-cradmin-groupitemvalue-status').alltext_normalized)

    def test_grouplist_status_waiting_for_feedback_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=3)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=timezone.now() - timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser)
        self.assertFalse(
                mockresponse.selector.exists(
                        '.devilry-cradmin-groupitemvalue '
                        '.devilry-cradmin-groupitemvalue-grade'))
        self.assertEqual(
                'Status: waiting for feedback',
                mockresponse.selector.one(
                        '.devilry-cradmin-groupitemvalue '
                        '.devilry-cradmin-groupitemvalue-status').alltext_normalized)

    def test_grouplist_status_corrected_show_grade_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=3)
        devilry_group_baker_factories.feedbackset_new_attempt_published(
            group=testgroup, grading_points=2)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser)
        self.assertFalse(
                mockresponse.selector.exists(
                        '.devilry-cradmin-groupitemvalue '
                        '.devilry-cradmin-groupitemvalue-status'))
        self.assertEqual(
                'Grade: passed',
                mockresponse.selector.one(
                        '.devilry-cradmin-groupitemvalue '
                        '.devilry-cradmin-groupitemvalue-grade').alltext_normalized)

    def test_grouplist_comments_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        feedbackset = devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
            group=testgroup)
        baker.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   text='asd',
                   user_role=Comment.USER_ROLE_STUDENT,
                   _quantity=2)
        baker.make('devilry_comment.CommentFile',
                   comment=baker.make('devilry_group.GroupComment',
                                      feedback_set=feedbackset,
                                      visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                                      comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                      user_role=Comment.USER_ROLE_STUDENT))
        baker.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   user_role=Comment.USER_ROLE_EXAMINER,
                   _quantity=5)
        baker.make('devilry_group.GroupComment',  # Should not be part of count
                   feedback_set=feedbackset,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   user_role=Comment.USER_ROLE_EXAMINER)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                '2 comments from student. 1 file from student. 5 comments from examiner.',
                mockresponse.selector.one(
                        '.devilry-cradmin-groupitemvalue '
                        '.devilry-cradmin-groupitemvalue-comments').alltext_normalized)

    def test_allperiods_link_label(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                'Your courses',
                mockresponse.selector.one('#devilry_student_dashboard_allperiods_link').alltext_normalized)

    def test_link_urls(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(1, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
        self.assertEqual(
                mock.call(appname='allperiods', args=(), viewname='INDEX', kwargs={}),
                mockresponse.request.cradmin_instance.reverse_url.call_args_list[0])

    def test_no_pagination(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate', relatedstudent__user=testuser,
                   assignment_group__parentnode__parentnode__start_time=ACTIVE_PERIOD_START,
                   assignment_group__parentnode__parentnode__end_time=ACTIVE_PERIOD_END,
                   _quantity=dashboard.DashboardView.paginate_by)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertFalse(mockresponse.selector.exists('.cradmin-legacy-loadmorepager'))

    def test_pagination(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Candidate', relatedstudent__user=testuser,
                   assignment_group__parentnode__parentnode__start_time=ACTIVE_PERIOD_START,
                   assignment_group__parentnode__parentnode__end_time=ACTIVE_PERIOD_END,
                   _quantity=dashboard.DashboardView.paginate_by + 1)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertTrue(mockresponse.selector.exists('.cradmin-legacy-loadmorepager'))

    def test_querycount(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment1 = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testassignment2 = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        loops = dashboard.DashboardView.paginate_by / 2
        for number in range(int(round(loops))):
            group1 = baker.make('core.AssignmentGroup', parentnode=testassignment1)
            baker.make('core.Examiner', assignmentgroup=group1)
            baker.make('core.Candidate', relatedstudent__user=testuser, assignment_group=group1)
            devilry_group_baker_factories.feedbackset_first_attempt_published(
                group=group1, grading_points=1)

            group2 = baker.make('core.AssignmentGroup', parentnode=testassignment2)
            baker.make('core.Examiner', assignmentgroup=group2)
            baker.make('core.Candidate', relatedstudent__user=testuser, assignment_group=group2)
            devilry_group_baker_factories.feedbackset_first_attempt_published(
                group=group2, grading_points=1)
        with self.assertNumQueries(12):
            mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                loops * 2,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_querycount_points_to_grade_mapper_custom_table(self):
        testuser = baker.make(settings.AUTH_USER_MODEL,
                              fullname='testuser')
        testassignment1 = baker.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE)
        point_to_grade_map1 = baker.make('core.PointToGradeMap',
                                         assignment=testassignment1, invalid=False)
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map1,
                   minimum_points=0, maximum_points=1)
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map1,
                   minimum_points=2, maximum_points=3)
        testassignment2 = baker.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE)
        point_to_grade_map2 = baker.make('core.PointToGradeMap',
                                         assignment=testassignment2, invalid=False)
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map2,
                   minimum_points=0, maximum_points=1)

        loops = dashboard.DashboardView.paginate_by / 2
        for number in range(int(round(loops))):
            group1 = baker.make('core.AssignmentGroup', parentnode=testassignment1)
            baker.make('core.Candidate', relatedstudent__user=testuser, assignment_group=group1)
            devilry_group_baker_factories.feedbackset_first_attempt_published(
                group=group1, grading_points=1)

            group2 = baker.make('core.AssignmentGroup', parentnode=testassignment2)
            baker.make('core.Candidate', relatedstudent__user=testuser, assignment_group=group2)
            devilry_group_baker_factories.feedbackset_first_attempt_published(
                group=group2, grading_points=1)
        with self.assertNumQueries(14):
            mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                loops * 2,
                self.__get_assignment_count(selector=mockresponse.selector))
