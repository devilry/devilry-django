import htmls
from datetime import datetime
from django import test
from django.conf import settings
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url
from model_mommy import mommy

from devilry.apps.core import devilry_core_mommy_factories
from devilry.apps.core.models import Assignment
from devilry.devilry_comment.models import Comment
from devilry.devilry_examiner.views.assignment import grouplist
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group.models import GroupComment


class TestGroupItemValue(test.TestCase):
    def test_title(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__fullname='Test User',
                   relatedstudent__user__shortname='testuser@example.com')
        selector = htmls.S(grouplist.GroupItemValue(value=testgroup).render())
        self.assertEqual(
            'Test User(testuser@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_title_anonymous(self):
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        selector = htmls.S(grouplist.GroupItemValue(value=testgroup).render())
        self.assertEqual(
            'MyAnonymousID',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)


class TestAssignmentListView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = grouplist.GroupListView

    def test_title(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment One')
        mommy.make('core.Examiner', relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                                          requestuser=testuser)
        self.assertIn(
            'Assignment One',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           long_name='Assignment One')
        mommy.make('core.Examiner', relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                                          requestuser=testuser)
        self.assertEqual(
            'Assignment One',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_not_groups_where_not_examiner(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mommy.make('core.Examiner',
                   assignmentgroup__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                                          requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_groups_sanity(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mommy.make('core.Examiner', relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mommy.make('core.Examiner', relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                                          requestuser=testuser)
        self.assertEqual(
            2,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_anonymizationmode_off_candidates(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF))
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='unanonymizedfullname',
                   relatedstudent__user__fullname='A un-anonymized fullname',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup.assignment,
                                                          requestuser=testuser)
        self.assertIn('unanonymizedfullname', mockresponse.response.content)
        self.assertIn('A un-anonymized fullname', mockresponse.response.content)
        self.assertNotIn('MyAnonymousID', mockresponse.response.content)

    def test_anonymizationmode_semi_anonymous_candidates(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='unanonymizedfullname',
                   relatedstudent__user__fullname='A un-anonymized fullname',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup.assignment,
                                                          requestuser=testuser)
        self.assertNotIn('unanonymizedfullname', mockresponse.response.content)
        self.assertNotIn('A un-anonymized fullname', mockresponse.response.content)
        self.assertIn('MyAnonymousID', mockresponse.response.content)

    def test_anonymizationmode_fully_anonymous_candidates(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS))
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='unanonymizedfullname',
                   relatedstudent__user__fullname='A un-anonymized fullname',
                   relatedstudent__automatic_anonymous_id='MyAnonymousID')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup.assignment,
                                                          requestuser=testuser)
        self.assertNotIn('unanonymizedfullname', mockresponse.response.content)
        self.assertNotIn('A un-anonymized fullname', mockresponse.response.content)
        self.assertIn('MyAnonymousID', mockresponse.response.content)

    def test_querycount(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mommy.make('core.Examiner', relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment,
                   _quantity=20)
        with self.assertNumQueries(2):
            self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                               requestuser=testuser)

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

    def test_group_render_group_url(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                                          requestuser=testuser)
        self.assertEqual(
            reverse_cradmin_url(
                instanceid='devilry_group_examiner',
                appname='feedbackfeed',
                roleid=testgroup.id,
                viewname=crapp.INDEXVIEW_NAME,
            ),
            mockresponse.selector.one('a.django-cradmin-listbuilder-itemframe')['href'])

    def test_search_nomatch(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start'))
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
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_search_match_fullname(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start'))
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
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_search_match_shortname(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start'))
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
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_search_anonymous_nomatch_fullname(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
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
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_search_anonymous_nomatch_shortname(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
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
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_search_anonymous_nomatch_candidate_id_from_candidate(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
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
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_search_anonymous_match_automatic_candidate_id_from_relatedstudent(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
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
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_search_anonymous_match_automatic_anonymous_id(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
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
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_fullname(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   uses_custom_candidate_ids=True,
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
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
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_shortname(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   uses_custom_candidate_ids=True,
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
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
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_automatic_candidate_id_from_relatedstudent(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   uses_custom_candidate_ids=True,
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
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
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_nomatch_automatic_anonymous_id(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   uses_custom_candidate_ids=True,
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
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
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_search_anonymous_uses_custom_candidate_ids_match_candidate_id_from_candidate(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   uses_custom_candidate_ids=True,
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
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
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def __get_titles(self, selector):
        return [
            element.alltext_normalized
            for element in selector.list(
                '.django-cradmin-listbuilder-itemvalue-titledescription-title')]

    def test_orderby_default(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='b',
                   relatedstudent__user__fullname='A')
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__user__shortname='a',
                   relatedstudent__user__fullname='B')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser)
        self.assertEqual(
            ['A(b)', 'B(a)'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_name_descending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='b',
                   relatedstudent__user__fullname='A')
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__user__shortname='a',
                   relatedstudent__user__fullname='B')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-name_descending'},
            requestuser=testuser)
        self.assertEqual(
            ['B(a)', 'A(b)'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_default_anonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__automatic_anonymous_id='c')
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__automatic_anonymous_id='b',
                   relatedstudent__candidate_id='A')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser)
        self.assertEqual(
            ['A', 'c'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_name_descending_anonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__automatic_anonymous_id='c')
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__automatic_anonymous_id='b',
                   relatedstudent__candidate_id='A')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-name_descending'},
            requestuser=testuser)
        self.assertEqual(
            ['c', 'A'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_default_anonymous_uses_custom_candidate_ids(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   candidate_id='b')
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   candidate_id='a')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser)
        self.assertEqual(
            ['a', 'b'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_name_descending_anonymous_uses_custom_candidate_ids(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   candidate_id='b')
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   candidate_id='a')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-name_descending'},
            requestuser=testuser)
        self.assertEqual(
            ['b', 'a'],
            self.__get_titles(mockresponse.selector))

    def __has_orderby_option_label(self, selector, orderby_option_label):
        order_by_labels = {element.alltext_normalized
                           for element in selector.list('#django_cradmin_listfilter_orderby option')}
        return orderby_option_label in order_by_labels

    def test_orderby_shortname_ascending_rendered_in_nonanonymous_email(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=testuser)
        self.assertTrue(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Email'))
        self.assertFalse(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Username'))

    def test_orderby_shortname_ascending_rendered_in_nonanonymous_username(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=testuser)
        self.assertFalse(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Email'))
        self.assertTrue(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Username'))

    def test_orderby_shortname_ascending_not_rendered_in_anonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=testuser)
        self.assertFalse(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Email'))

    def test_orderby_shortname_ascending_not_rendered_in_anonymous_uses_custom_candidate_ids(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=testuser)
        self.assertFalse(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Email'))

    def test_orderby_shortname_ascending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='b')
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__user__shortname='a')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-shortname_ascending'},
            requestuser=testuser)
        self.assertEqual(
            ['a', 'b'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_shortname_descending_rendered_in_nonanonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=testuser)
        self.assertTrue(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Email (descending)'))

    def test_orderby_shortname_descending_not_rendered_in_anonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=testuser)
        self.assertFalse(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Email (descending)'))

    def test_orderby_shortname_descending_not_rendered_in_anonymous_uses_custom_candidate_ids(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                requestuser=testuser)
        self.assertFalse(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Email (descending)'))

    def test_orderby_shortname_descending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='b')
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__user__shortname='a')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-shortname_descending'},
            requestuser=testuser)
        self.assertEqual(
            ['b', 'a'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_lastname_ascending_rendered_in_nonanonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser)
        self.assertTrue(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Last name'))

    def test_orderby_lastname_ascending_not_rendered_in_anonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser)
        self.assertFalse(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Last name'))

    def test_orderby_lastname_ascending_not_rendered_in_anonymous_uses_custom_candidate_ids(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser)
        self.assertFalse(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Last name'))

    def test_orderby_lastname_ascending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='user1',
                   relatedstudent__user__lastname='b')
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__user__shortname='user2',
                   relatedstudent__user__lastname='a')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-lastname_ascending'},
            requestuser=testuser)
        self.assertEqual(
            ['user2', 'user1'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_lastname_descending_rendered_in_nonanonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser)
        self.assertTrue(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Last name (descending)'))

    def test_orderby_lastname_descending_not_rendered_in_anonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser)
        self.assertFalse(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Last name (descending)'))

    def test_orderby_lastname_descending_not_rendered_in_anonymous_uses_custom_candidate_ids(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           uses_custom_candidate_ids=True,
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser)
        self.assertFalse(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Last name (descending)'))

    def test_orderby_lastname_descending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='user1',
                   relatedstudent__user__lastname='b')
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__user__shortname='user2',
                   relatedstudent__user__lastname='a')
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-lastname_descending'},
            requestuser=testuser)
        self.assertEqual(
            ['user1', 'user2'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_points_ascending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=testuser)

        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup1, grading_points=3)
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup2, grading_points=10)
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup3, grading_points=2)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-points_ascending'},
            requestuser=testuser)
        self.assertEqual(
            ['user3', 'user1', 'user2'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_points_descending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=testuser)

        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup1, grading_points=3)
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup2, grading_points=10)
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup3, grading_points=2)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-points_descending'},
            requestuser=testuser)
        self.assertEqual(
            ['user2', 'user1', 'user3'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_last_commented_by_student_ascending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup1,
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=datetime(2011, 12, 24, 0, 0))

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup2,
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=datetime(2010, 12, 24, 0, 0))
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-last_commented_by_student_ascending'},
            requestuser=testuser)
        self.assertEqual(
            ['user2', 'user1'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_last_commented_by_student_descending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup1,
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=datetime(2011, 12, 24, 0, 0))

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup2,
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=datetime(2010, 12, 24, 0, 0))
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-last_commented_by_student_descending'},
            requestuser=testuser)
        self.assertEqual(
            ['user1', 'user2'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_last_commented_by_examiner_ascending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup1,
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=datetime(2011, 12, 24, 0, 0))

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup2,
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=datetime(2010, 12, 24, 0, 0))
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-last_commented_by_examiner_ascending'},
            requestuser=testuser)
        self.assertEqual(
            ['user2', 'user1'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_last_commented_by_examiner_descending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup1,
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=datetime(2011, 12, 24, 0, 0))

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('devilry_group.GroupComment',
                   feedback_set__group=testgroup2,
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=datetime(2010, 12, 24, 0, 0))
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-last_commented_by_examiner_descending'},
            requestuser=testuser)
        self.assertEqual(
            ['user1', 'user2'],
            self.__get_titles(mockresponse.selector))
