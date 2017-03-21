from datetime import timedelta

import htmls
from django import test
from django.conf import settings
from django_cradmin import cradmin_testhelpers
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url
from model_mommy import mommy

from devilry.apps.core.mommy_recipes import ACTIVE_PERIOD_START
from devilry.devilry_examiner.views.dashboard import assignmentlist


class TestAssignmentItemValue(test.TestCase):
    def test_title(self):
        assignment = mommy.make('core.Assignment',
                                parentnode__parentnode__short_name='testsubject',
                                parentnode__short_name='testperiod',
                                long_name='Assignment One')
        assignment.waiting_for_feedback_count = 0
        selector = htmls.S(assignmentlist.AssignmentItemValue(value=assignment).render())
        self.assertEqual(
            'testsubject.testperiod - Assignment One',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description_none_waiting_for_feedback(self):
        assignment = mommy.make('core.Assignment')
        assignment.waiting_for_feedback_count = 0
        selector = htmls.S(assignmentlist.AssignmentItemValue(value=assignment).render())
        self.assertEqual(
            'Nobody waiting for feedback',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)
        self.assertTrue(
            selector.exists('.devilry-django-cradmin-listbuilder-itemvalue-titledescription-description-muted'))
        self.assertFalse(
            selector.exists('.devilry-django-cradmin-listbuilder-itemvalue-titledescription-description-warning'))

    def test_description_waiting_for_feedback(self):
        assignment = mommy.make('core.Assignment')
        assignment.waiting_for_feedback_count = 11
        selector = htmls.S(assignmentlist.AssignmentItemValue(value=assignment).render())
        self.assertEqual(
            '11 waiting for feedback',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)
        self.assertTrue(
            selector.exists('.devilry-django-cradmin-listbuilder-itemvalue-titledescription-description-warning'))
        self.assertFalse(
            selector.exists('.devilry-django-cradmin-listbuilder-itemvalue-titledescription-description-muted'))


class TestAssignmentListView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = assignmentlist.AssignmentListView

    def test_title(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertIn(
            'Examiner dashboard',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            'Examiner dashboard',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_page_subheader(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            'Listing of assigments where you are set as examiner.',
            mockresponse.selector.one('.devilry-page-subheader').alltext_normalized)

    def test_not_assignments_where_not_examiner(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_not_assignments_where_period_is_inactive(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe('devilry.apps.core.assignment_oldperiod_end'))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe('devilry.apps.core.assignment_futureperiod_start'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_assignments_where_period_is_active(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner', relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_assignments_no_duplicates(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mommy.make('core.Examiner', relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mommy.make('core.Examiner', relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_assignment_url(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mommy.make('core.Examiner', relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            reverse_cradmin_url(
                instanceid='devilry_examiner_assignment',
                appname='grouplist',
                roleid=testassignment.id,
                viewname=crapp.INDEXVIEW_NAME,
            ),
            mockresponse.selector.one('a.django-cradmin-listbuilder-itemframe')['href'])

    def test_render_search_nomatch(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-nomatch'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue-titledescription-title'))

    def test_render_search_match_subject_short_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       parentnode__parentnode__short_name='testsubject'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-testsubject'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue-titledescription-title'))

    def test_render_search_match_subject_long_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       parentnode__parentnode__long_name='Testsubject'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-Testsubject'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue-titledescription-title'))

    def test_render_search_match_period_short_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       parentnode__short_name='testperiod'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-testperiod'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue-titledescription-title'))

    def test_render_search_match_period_long_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       parentnode__long_name='Testperiod'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-Testperiod'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue-titledescription-title'))

    def test_render_search_match_assignment_short_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       short_name='testassignment'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-testassignment'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue-titledescription-title'))

    def test_render_search_match_assignment_long_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Testassignment'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-Testassignment'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue-titledescription-title'))

    def __get_titles(self, selector):
        return [
            element.alltext_normalized
            for element in selector.list(
                '.django-cradmin-listbuilder-itemvalue-titledescription-title')]

    def test_render_orderby_first_deadline_descending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod1 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject1',
                                        short_name='testperiod')
        testperiod2 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject2',
                                        short_name='testperiod')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       first_deadline=ACTIVE_PERIOD_START + timedelta(days=1),
                       parentnode=testperiod1))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 2',
                       first_deadline=ACTIVE_PERIOD_START + timedelta(days=3),
                       parentnode=testperiod1))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
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
            self.__get_titles(mockresponse.selector))

    def test_render_orderby_first_deadline_ascending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod1 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject1',
                                        short_name='testperiod')
        testperiod2 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject2',
                                        short_name='testperiod')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       first_deadline=ACTIVE_PERIOD_START + timedelta(days=1),
                       parentnode=testperiod1))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 2',
                       first_deadline=ACTIVE_PERIOD_START + timedelta(days=3),
                       parentnode=testperiod1))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       first_deadline=ACTIVE_PERIOD_START + timedelta(days=2),
                       parentnode=testperiod2))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'orderby-first_deadline_ascending'},
                requestuser=testuser)
        self.assertEqual(
            [
                'testsubject1.testperiod - Assignment 1',
                'testsubject2.testperiod - Assignment 1',
                'testsubject1.testperiod - Assignment 2',
            ],
            self.__get_titles(mockresponse.selector))

    def test_render_orderby_publishing_time_descending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod1 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject1',
                                        short_name='testperiod')
        testperiod2 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject2',
                                        short_name='testperiod')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       publishing_time=ACTIVE_PERIOD_START + timedelta(days=1),
                       parentnode=testperiod1))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 2',
                       publishing_time=ACTIVE_PERIOD_START + timedelta(days=3),
                       parentnode=testperiod1))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       publishing_time=ACTIVE_PERIOD_START + timedelta(days=2),
                       parentnode=testperiod2))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'orderby-publishing_time_descending'},
                requestuser=testuser)
        self.assertEqual(
            [
                'testsubject1.testperiod - Assignment 2',
                'testsubject2.testperiod - Assignment 1',
                'testsubject1.testperiod - Assignment 1',
            ],
            self.__get_titles(mockresponse.selector))

    def test_render_orderby_publishing_time_ascending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod1 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject1',
                                        short_name='testperiod')
        testperiod2 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject2',
                                        short_name='testperiod')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       publishing_time=ACTIVE_PERIOD_START + timedelta(days=1),
                       parentnode=testperiod1))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 2',
                       publishing_time=ACTIVE_PERIOD_START + timedelta(days=3),
                       parentnode=testperiod1))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       publishing_time=ACTIVE_PERIOD_START + timedelta(days=2),
                       parentnode=testperiod2))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'orderby-publishing_time_ascending'},
                requestuser=testuser)
        self.assertEqual(
            [
                'testsubject1.testperiod - Assignment 1',
                'testsubject2.testperiod - Assignment 1',
                'testsubject1.testperiod - Assignment 2',
            ],
            self.__get_titles(mockresponse.selector))

    def test_render_orderby_name_ascending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod1 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject1',
                                        short_name='testperiod')
        testperiod2 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject2',
                                        short_name='testperiod')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       parentnode=testperiod1))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       parentnode=testperiod2))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 2',
                       parentnode=testperiod1))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                requestuser=testuser,
                viewkwargs={'filters_string': 'orderby-name_ascending'})
        self.assertEqual(
            [
                'testsubject1.testperiod - Assignment 1',
                'testsubject1.testperiod - Assignment 2',
                'testsubject2.testperiod - Assignment 1',
            ],
            self.__get_titles(mockresponse.selector))

    def test_render_orderby_name_descending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testperiod1 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject1',
                                        short_name='testperiod')
        testperiod2 = mommy.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject2',
                                        short_name='testperiod')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       parentnode=testperiod1))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       parentnode=testperiod2))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=mommy.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 2',
                       parentnode=testperiod1))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                requestuser=testuser,
                viewkwargs={'filters_string': 'orderby-name_descending'})
        self.assertEqual(
            [
                'testsubject2.testperiod - Assignment 1',
                'testsubject1.testperiod - Assignment 2',
                'testsubject1.testperiod - Assignment 1',
            ],
            self.__get_titles(mockresponse.selector))

