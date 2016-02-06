from datetime import timedelta

from django import test
from django.conf import settings
from django_cradmin import cradmin_testhelpers
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url
from model_mommy import mommy

from devilry.apps.core.mommy_recipes import ACTIVE_PERIOD_START
from devilry.devilry_student.views.dashboard import dashboard


class TestDashboardView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = dashboard.DashboardView

    def test_title(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', relatedstudent__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertIn(
                'Student dashboard',
                mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', relatedstudent__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
                'Student dashboard',
                mockresponse.selector.one('h1').alltext_normalized)

    def test_page_subheader(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', relatedstudent__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
                'Welcome! Please select an assignment below to add deliveries, '
                'view feedback or communicate with you examiner.',
                mockresponse.selector.one('.devilry-page-subheader').alltext_normalized)

    def __test_assignment_count(self, selector):
        return selector.count('.devilry-cradmin-groupitemvalue')

    def test_not_assignments_where_not_student(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
                0,
                self.__test_assignment_count(selector=mockresponse.selector))

    def test_grouplist_not_future_periods(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe('devilry.apps.core.assignment_futureperiod_start'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
                0,
                self.__test_assignment_count(selector=mockresponse.selector))

    def test_grouplist_not_old_periods(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe('devilry.apps.core.assignment_oldperiod_end'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
                0,
                self.__test_assignment_count(selector=mockresponse.selector))

    def test_grouplist_include_active_periods(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
                1,
                self.__test_assignment_count(selector=mockresponse.selector))

    def test_assignment_url(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testcandidate = mommy.make('core.Candidate', relatedstudent__user=testuser,
                                   assignment_group__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
                reverse_cradmin_url(
                        instanceid='devilry_group_student',
                        appname='feedbackfeed',
                        roleid=testcandidate.assignment_group_id,
                        viewname=crapp.INDEXVIEW_NAME,
                ),
                mockresponse.selector.one('a.devilry-student-listbuilder-grouplist-itemframe')['href'])

    def test_grouplist_search_nomatch(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-nomatch'},
                requestuser=testuser)
        self.assertEqual(
                0,
                self.__test_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_subject_short_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode__parentnode__short_name='testsubject'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-testsubject'},
                requestuser=testuser)
        self.assertEqual(
                1,
                self.__test_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_subject_long_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode__parentnode__long_name='Testsubject'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-Testsubject'},
                requestuser=testuser)
        self.assertEqual(
                1,
                self.__test_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_period_short_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode__short_name='testperiod'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-testperiod'},
                requestuser=testuser)
        self.assertEqual(
                1,
                self.__test_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_period_long_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode__long_name='Testperiod'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-Testperiod'},
                requestuser=testuser)
        self.assertEqual(
                1,
                self.__test_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_assignment_short_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           short_name='testassignment'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-testassignment'},
                requestuser=testuser)
        self.assertEqual(
                1,
                self.__test_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_assignment_long_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           long_name='Testassignment'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-Testassignment'},
                requestuser=testuser)
        self.assertEqual(
                1,
                self.__test_assignment_count(selector=mockresponse.selector))

    def __get_assignment_titles(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.devilry-cradmin-groupitemvalue '
                                             '.django-cradmin-listbuilder-itemvalue-titledescription-title')]

    def test_grouplist_orderby(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod1 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject1',
                                        short_name='testperiod')
        testperiod2 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject2',
                                        short_name='testperiod')
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           long_name='Assignment 1',
                           first_deadline=ACTIVE_PERIOD_START + timedelta(days=1),
                           parentnode=testperiod1))
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           long_name='Assignment 2',
                           first_deadline=ACTIVE_PERIOD_START + timedelta(days=3),
                           parentnode=testperiod1))
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           long_name='Assignment 1',
                           first_deadline=ACTIVE_PERIOD_START + timedelta(days=2),
                           parentnode=testperiod2))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                requestuser=testuser)
        self.assertEqual(
                [
                    'testsubject1.testperiod - Assignment 2',
                    'testsubject2.testperiod - Assignment 1',
                    'testsubject1.testperiod - Assignment 1',
                ],
                self.__get_assignment_titles(mockresponse.selector))
