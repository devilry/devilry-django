import htmls
from django import test
from django.conf import settings
from django_cradmin import cradmin_testhelpers
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url
from model_mommy import mommy

from devilry.apps.core.models import Assignment
from devilry.devilry_examiner.views.assignment import grouplist


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

    # def __get_titles(self, selector):
    #     return [
    #         element.alltext_normalized
    #         for element in selector.list(
    #             '.django-cradmin-listbuilder-itemvalue-titledescription-title')]
    #
    # def test_render_orderby_default(self):
    #     testuser = mommy.make(settings.AUTH_USER_MODEL)
    #     testperiod1 = mommy.make_recipe('devilry.apps.core.period_active',
    #                                     parentnode__short_name='testsubject1',
    #                                     short_name='testperiod')
    #     testperiod2 = mommy.make_recipe('devilry.apps.core.period_active',
    #                                     parentnode__short_name='testsubject2',
    #                                     short_name='testperiod')
    #     mommy.make('core.Examiner',
    #                relatedexaminer__user=testuser,
    #                assignmentgroup__parentnode=mommy.make_recipe(
    #                    'devilry.apps.core.assignment_activeperiod_start',
    #                    long_name='Assignment 1',
    #                    publishing_time=ACTIVE_PERIOD_START + timedelta(days=1),
    #                    parentnode=testperiod1))
    #     mommy.make('core.Examiner',
    #                relatedexaminer__user=testuser,
    #                assignmentgroup__parentnode=mommy.make_recipe(
    #                    'devilry.apps.core.assignment_activeperiod_start',
    #                    long_name='Assignment 2',
    #                    publishing_time=ACTIVE_PERIOD_START + timedelta(days=3),
    #                    parentnode=testperiod1))
    #     mommy.make('core.Examiner',
    #                relatedexaminer__user=testuser,
    #                assignmentgroup__parentnode=mommy.make_recipe(
    #                    'devilry.apps.core.assignment_activeperiod_start',
    #                    long_name='Assignment 1',
    #                    publishing_time=ACTIVE_PERIOD_START + timedelta(days=2),
    #                    parentnode=testperiod2))
    #     mockresponse = self.mock_http200_getrequest_htmls(
    #             cradmin_role=testassignment,
    #             requestuser=testuser)
    #     self.assertEqual(
    #         [
    #             'testsubject1.testperiod - Assignment 2',
    #             'testsubject2.testperiod - Assignment 1',
    #             'testsubject1.testperiod - Assignment 1',
    #         ],
    #         self.__get_titles(mockresponse.selector))
    #
    # def test_render_orderby_publishing_time_descending(self):
    #     testuser = mommy.make(settings.AUTH_USER_MODEL)
    #     testperiod1 = mommy.make_recipe('devilry.apps.core.period_active',
    #                                     parentnode__short_name='testsubject1',
    #                                     short_name='testperiod')
    #     testperiod2 = mommy.make_recipe('devilry.apps.core.period_active',
    #                                     parentnode__short_name='testsubject2',
    #                                     short_name='testperiod')
    #     mommy.make('core.Examiner',
    #                relatedexaminer__user=testuser,
    #                assignmentgroup__parentnode=mommy.make_recipe(
    #                    'devilry.apps.core.assignment_activeperiod_start',
    #                    long_name='Assignment 1',
    #                    publishing_time=ACTIVE_PERIOD_START + timedelta(days=1),
    #                    parentnode=testperiod1))
    #     mommy.make('core.Examiner',
    #                relatedexaminer__user=testuser,
    #                assignmentgroup__parentnode=mommy.make_recipe(
    #                    'devilry.apps.core.assignment_activeperiod_start',
    #                    long_name='Assignment 2',
    #                    publishing_time=ACTIVE_PERIOD_START + timedelta(days=3),
    #                    parentnode=testperiod1))
    #     mommy.make('core.Examiner',
    #                relatedexaminer__user=testuser,
    #                assignmentgroup__parentnode=mommy.make_recipe(
    #                    'devilry.apps.core.assignment_activeperiod_start',
    #                    long_name='Assignment 1',
    #                    publishing_time=ACTIVE_PERIOD_START + timedelta(days=2),
    #                    parentnode=testperiod2))
    #     mockresponse = self.mock_http200_getrequest_htmls(
    #             cradmin_role=testassignment,
    #             viewkwargs={'filters_string': 'orderby-publishing_time_descending'},
    #             requestuser=testuser)
    #     self.assertEqual(
    #         [
    #             'testsubject1.testperiod - Assignment 1',
    #             'testsubject2.testperiod - Assignment 1',
    #             'testsubject1.testperiod - Assignment 2',
    #         ],
    #         self.__get_titles(mockresponse.selector))
    #
    # def test_render_orderby_name_ascending(self):
    #     testuser = mommy.make(settings.AUTH_USER_MODEL)
    #     testperiod1 = mommy.make_recipe('devilry.apps.core.period_active',
    #                                     parentnode__short_name='testsubject1',
    #                                     short_name='testperiod')
    #     testperiod2 = mommy.make_recipe('devilry.apps.core.period_active',
    #                                     parentnode__short_name='testsubject2',
    #                                     short_name='testperiod')
    #     mommy.make('core.Examiner',
    #                relatedexaminer__user=testuser,
    #                assignmentgroup__parentnode=mommy.make_recipe(
    #                    'devilry.apps.core.assignment_activeperiod_start',
    #                    long_name='Assignment 1',
    #                    parentnode=testperiod1))
    #     mommy.make('core.Examiner',
    #                relatedexaminer__user=testuser,
    #                assignmentgroup__parentnode=mommy.make_recipe(
    #                    'devilry.apps.core.assignment_activeperiod_start',
    #                    long_name='Assignment 1',
    #                    parentnode=testperiod2))
    #     mommy.make('core.Examiner',
    #                relatedexaminer__user=testuser,
    #                assignmentgroup__parentnode=mommy.make_recipe(
    #                    'devilry.apps.core.assignment_activeperiod_start',
    #                    long_name='Assignment 2',
    #                    parentnode=testperiod1))
    #     mockresponse = self.mock_http200_getrequest_htmls(
    #             cradmin_role=testassignment,
    #             requestuser=testuser,
    #             viewkwargs={'filters_string': 'orderby-name_ascending'})
    #     self.assertEqual(
    #         [
    #             'testsubject1.testperiod - Assignment 1',
    #             'testsubject1.testperiod - Assignment 2',
    #             'testsubject2.testperiod - Assignment 1',
    #         ],
    #         self.__get_titles(mockresponse.selector))
    #
    # def test_render_orderby_name_descending(self):
    #     testuser = mommy.make(settings.AUTH_USER_MODEL)
    #     testperiod1 = mommy.make_recipe('devilry.apps.core.period_active',
    #                                     parentnode__short_name='testsubject1',
    #                                     short_name='testperiod')
    #     testperiod2 = mommy.make_recipe('devilry.apps.core.period_active',
    #                                     parentnode__short_name='testsubject2',
    #                                     short_name='testperiod')
    #     mommy.make('core.Examiner',
    #                relatedexaminer__user=testuser,
    #                assignmentgroup__parentnode=mommy.make_recipe(
    #                    'devilry.apps.core.assignment_activeperiod_start',
    #                    long_name='Assignment 1',
    #                    parentnode=testperiod1))
    #     mommy.make('core.Examiner',
    #                relatedexaminer__user=testuser,
    #                assignmentgroup__parentnode=mommy.make_recipe(
    #                    'devilry.apps.core.assignment_activeperiod_start',
    #                    long_name='Assignment 1',
    #                    parentnode=testperiod2))
    #     mommy.make('core.Examiner',
    #                relatedexaminer__user=testuser,
    #                assignmentgroup__parentnode=mommy.make_recipe(
    #                    'devilry.apps.core.assignment_activeperiod_start',
    #                    long_name='Assignment 2',
    #                    parentnode=testperiod1))
    #     mockresponse = self.mock_http200_getrequest_htmls(
    #             cradmin_role=testassignment,
    #             requestuser=testuser,
    #             viewkwargs={'filters_string': 'orderby-name_descending'})
    #     self.assertEqual(
    #         [
    #             'testsubject2.testperiod - Assignment 1',
    #             'testsubject1.testperiod - Assignment 2',
    #             'testsubject1.testperiod - Assignment 1',
    #         ],
    #         self.__get_titles(mockresponse.selector))
    #
