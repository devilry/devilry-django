from datetime import timedelta

import htmls
from django import test
from django.conf import settings
from cradmin_legacy import cradmin_testhelpers
from cradmin_legacy import crapp
from cradmin_legacy.crinstance import reverse_cradmin_url
from model_bakery import baker

from devilry.apps.core.baker_recipes import ACTIVE_PERIOD_START
from devilry.devilry_examiner.views.dashboard import assignmentlist


class TestAssignmentItemValue(test.TestCase):
    def test_title(self):
        assignment = baker.make('core.Assignment',
                                parentnode__parentnode__short_name='testsubject',
                                parentnode__short_name='testperiod',
                                long_name='Assignment One')
        assignment.waiting_for_feedback_count = 0
        selector = htmls.S(assignmentlist.AssignmentItemValue(value=assignment).render())
        self.assertEqual(
            'testsubject.testperiod - Assignment One',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description_none_waiting_for_feedback(self):
        assignment = baker.make('core.Assignment')
        assignment.waiting_for_feedback_count = 0
        selector = htmls.S(assignmentlist.AssignmentItemValue(value=assignment).render())
        self.assertEqual(
            'Nobody waiting for feedback',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized)
        self.assertTrue(
            selector.exists('.devilry-cradmin-legacy-listbuilder-itemvalue-titledescription-description-muted'))
        self.assertFalse(
            selector.exists('.devilry-cradmin-legacy-listbuilder-itemvalue-titledescription-description-warning'))

    def test_description_waiting_for_feedback(self):
        assignment = baker.make('core.Assignment')
        assignment.waiting_for_feedback_count = 11
        selector = htmls.S(assignmentlist.AssignmentItemValue(value=assignment).render())
        self.assertEqual(
            '11 waiting for feedback',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized)
        self.assertTrue(
            selector.exists('.devilry-cradmin-legacy-listbuilder-itemvalue-titledescription-description-warning'))
        self.assertFalse(
            selector.exists('.devilry-cradmin-legacy-listbuilder-itemvalue-titledescription-description-muted'))


class TestAssignmentListView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = assignmentlist.AssignmentListView

    def test_title(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertIn(
            'Examiner dashboard',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            'Examiner dashboard',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_page_subheader(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', relatedexaminer__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            'Listing of assigments where you are set as examiner.',
            mockresponse.selector.one('.devilry-page-subheader').alltext_normalized)

    def test_not_assignments_where_not_examiner(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'))

    def test_not_assignments_where_period_is_inactive(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe('devilry.apps.core.assignment_oldperiod_end'))
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe('devilry.apps.core.assignment_futureperiod_start'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'))

    def test_assignments_where_period_is_active(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner', relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'))

    def test_assignments_no_duplicates(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        baker.make('core.Examiner', relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        baker.make('core.Examiner', relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testuser,
                                                          requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'))

    def test_assignment_url(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        baker.make('core.Examiner', relatedexaminer__user=testuser,
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
            mockresponse.selector.one('a.cradmin-legacy-listbuilder-itemframe')['href'])

    def test_render_search_nomatch(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-nomatch'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue-titledescription-title'))

    def test_render_search_match_subject_short_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       parentnode__parentnode__short_name='testsubject'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-testsubject'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue-titledescription-title'))

    def test_render_search_match_subject_long_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       parentnode__parentnode__long_name='Testsubject'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-Testsubject'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue-titledescription-title'))

    def test_render_search_match_period_short_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       parentnode__short_name='testperiod'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-testperiod'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue-titledescription-title'))

    def test_render_search_match_period_long_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       parentnode__long_name='Testperiod'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-Testperiod'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue-titledescription-title'))

    def test_render_search_match_assignment_short_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       short_name='testassignment'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-testassignment'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue-titledescription-title'))

    def test_render_search_match_assignment_long_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Testassignment'))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testuser,
                viewkwargs={'filters_string': 'search-Testassignment'},
                requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue-titledescription-title'))

    def __get_titles(self, selector):
        return [
            element.alltext_normalized
            for element in selector.list(
                '.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]

    def test_render_orderby_first_deadline_descending(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod1 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject1',
                                        short_name='testperiod')
        testperiod2 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject2',
                                        short_name='testperiod')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       first_deadline=ACTIVE_PERIOD_START + timedelta(days=1),
                       parentnode=testperiod1))
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 2',
                       first_deadline=ACTIVE_PERIOD_START + timedelta(days=3),
                       parentnode=testperiod1))
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
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
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod1 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject1',
                                        short_name='testperiod')
        testperiod2 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject2',
                                        short_name='testperiod')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       first_deadline=ACTIVE_PERIOD_START + timedelta(days=1),
                       parentnode=testperiod1))
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 2',
                       first_deadline=ACTIVE_PERIOD_START + timedelta(days=3),
                       parentnode=testperiod1))
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
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
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod1 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject1',
                                        short_name='testperiod')
        testperiod2 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject2',
                                        short_name='testperiod')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       publishing_time=ACTIVE_PERIOD_START + timedelta(days=1),
                       parentnode=testperiod1))
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 2',
                       publishing_time=ACTIVE_PERIOD_START + timedelta(days=3),
                       parentnode=testperiod1))
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
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
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod1 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject1',
                                        short_name='testperiod')
        testperiod2 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject2',
                                        short_name='testperiod')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       publishing_time=ACTIVE_PERIOD_START + timedelta(days=1),
                       parentnode=testperiod1))
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 2',
                       publishing_time=ACTIVE_PERIOD_START + timedelta(days=3),
                       parentnode=testperiod1))
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
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
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod1 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject1',
                                        short_name='testperiod')
        testperiod2 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject2',
                                        short_name='testperiod')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       parentnode=testperiod1))
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       parentnode=testperiod2))
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
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
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod1 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject1',
                                        short_name='testperiod')
        testperiod2 = baker.make_recipe('devilry.apps.core.period_active',
                                        parentnode__short_name='testsubject2',
                                        short_name='testperiod')
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       parentnode=testperiod1))
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
                       'devilry.apps.core.assignment_activeperiod_start',
                       long_name='Assignment 1',
                       parentnode=testperiod2))
        baker.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=baker.make_recipe(
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

    def test_selfassign_user_not_related_examiner_on_period_sanity(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        baker.make('core.AssignmentGroup', parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=examiner_user,
            requestuser=examiner_user
        )
        self.assertFalse(mockresponse.selector.exists('#id-devilry-examiner-selfassign-section'))
    
    def test_selfassign_period_not_active_ended(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_oldperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=examiner_user,
            requestuser=examiner_user
        )
        self.assertFalse(mockresponse.selector.exists('#id-devilry-examiner-selfassign-section'))

    def test_selfassign_period_not_active_not_started(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_futureperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=examiner_user,
            requestuser=examiner_user
        )
        self.assertFalse(mockresponse.selector.exists('#id-devilry-examiner-selfassign-section'))
    
    def test_selfassign_period_accessible_text_sanity(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=examiner_user,
            requestuser=examiner_user
        )
        self.assertTrue(mockresponse.selector.exists('#id-devilry-examiner-selfassign-section'))
        self.assertIn(
            'Add me to assignments',
            mockresponse.selector.one('#id-devilry-examiner-selfassign-section').alltext_normalized
        )
        self.assertIn(
            'Semesters with assignments available for self-assign:',
            mockresponse.selector.one('#id-devilry-examiner-selfassign-section').alltext_normalized
        )
        self.assertEqual(
            reverse_cradmin_url(
                instanceid='devilry_examiner_selfassign',
                appname='self-assign',
                roleid=assignment.parentnode.id,
                viewname=crapp.INDEXVIEW_NAME,
            ),
            mockresponse.selector.list('#id-devilry-examiner-selfassign-section-links > a')[0]['href'])

    def test_selfassign_single_period_accessible_sanity(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=examiner_user,
            requestuser=examiner_user
        )
        self.assertTrue(mockresponse.selector.exists('#id-devilry-examiner-selfassign-section'))
        selfassign_links = mockresponse.selector.list('#id-devilry-examiner-selfassign-section-links > a')
        self.assertEqual(len(selfassign_links), 1)
        self.assertEqual(
            selfassign_links[0].alltext_normalized,
            f'{assignment.parentnode.parentnode.long_name} - {assignment.parentnode.long_name}'
        )
        self.assertEqual(
            reverse_cradmin_url(
                instanceid='devilry_examiner_selfassign',
                appname='self-assign',
                roleid=assignment.parentnode.id,
                viewname=crapp.INDEXVIEW_NAME,
            ),
            mockresponse.selector.list('#id-devilry-examiner-selfassign-section-links > a')[0]['href'])

    def test_selfassign_multiple_periods_accessible_sanity(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment1 = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        assignment2 = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment Two',
            examiners_can_self_assign=True
        )
        baker.make('core.RelatedExaminer', period=assignment1.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment1)
        baker.make('core.RelatedExaminer', period=assignment2.parentnode, user=examiner_user)
        baker.make('core.AssignmentGroup', parentnode=assignment2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=examiner_user,
            requestuser=examiner_user
        )
        self.assertTrue(mockresponse.selector.exists('#id-devilry-examiner-selfassign-section'))
        selfassign_links = mockresponse.selector.list('#id-devilry-examiner-selfassign-section-links > a')
        self.assertEqual(len(selfassign_links), 2)
        self.assertEqual(
            selfassign_links[0].alltext_normalized,
            f'{assignment1.parentnode.parentnode.long_name} - {assignment1.parentnode.long_name}'
        )
        self.assertEqual(
            reverse_cradmin_url(
                instanceid='devilry_examiner_selfassign',
                appname='self-assign',
                roleid=assignment1.parentnode.id,
                viewname=crapp.INDEXVIEW_NAME,
            ),
            mockresponse.selector.list('#id-devilry-examiner-selfassign-section-links > a')[0]['href'])
        self.assertEqual(
            selfassign_links[1].alltext_normalized,
            f'{assignment2.parentnode.parentnode.long_name} - {assignment2.parentnode.long_name}'
        )
        self.assertEqual(
            reverse_cradmin_url(
                instanceid='devilry_examiner_selfassign',
                appname='self-assign',
                roleid=assignment2.parentnode.id,
                viewname=crapp.INDEXVIEW_NAME,
            ),
            mockresponse.selector.list('#id-devilry-examiner-selfassign-section-links > a')[1]['href'])

    def test_selfassign_period_accessible_user_already_examiner(self):
        examiner_user = baker.make(settings.AUTH_USER_MODEL)
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            long_name='Assignment One',
            examiners_can_self_assign=True
        )
        relatedexaminer = baker.make('core.RelatedExaminer', period=assignment.parentnode, user=examiner_user)
        group = baker.make('core.AssignmentGroup', parentnode=assignment)
        baker.make('core.Examiner', assignmentgroup=group, relatedexaminer=relatedexaminer)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=examiner_user,
            requestuser=examiner_user
        )
        self.assertTrue(mockresponse.selector.exists('#id-devilry-examiner-selfassign-section'))
        selfassign_links = mockresponse.selector.list('#id-devilry-examiner-selfassign-section-links > a')
        self.assertEqual(len(selfassign_links), 1)
        self.assertEqual(
            selfassign_links[0].alltext_normalized,
            f'{assignment.parentnode.parentnode.long_name} - {assignment.parentnode.long_name}'
        )
        self.assertEqual(
            reverse_cradmin_url(
                instanceid='devilry_examiner_selfassign',
                appname='self-assign',
                roleid=assignment.parentnode.id,
                viewname=crapp.INDEXVIEW_NAME,
            ),
            mockresponse.selector.list('#id-devilry-examiner-selfassign-section-links > a')[0]['href'])
