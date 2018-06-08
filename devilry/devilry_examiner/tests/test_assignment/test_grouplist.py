from datetime import datetime, timedelta

from django import test
from django.conf import settings
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url
from model_mommy import mommy

from devilry.apps.core import devilry_core_mommy_factories
from devilry.apps.core.models import Assignment
from devilry.apps.core.mommy_recipes import ACTIVE_PERIOD_END, ACTIVE_PERIOD_START
from devilry.devilry_comment.models import Comment
from devilry.devilry_examiner.views.assignment import grouplist
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group.models import GroupComment, ImageAnnotationComment
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestAssignmentListView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = grouplist.GroupListView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

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
        testuser = mommy.make(settings.AUTH_USER_MODEL,
                              fullname='testuser')
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        for number in range(30):
            group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
            mommy.make('core.Examiner',
                       relatedexaminer__user=testuser,
                       assignmentgroup=group)
            mommy.make('core.Examiner',
                       relatedexaminer__user__fullname='examiner{}'.format(number),
                       assignmentgroup=group)
            mommy.make('core.Candidate',
                       relatedstudent__user__fullname='candidate{}'.format(number),
                       assignment_group=group)
        with self.assertNumQueries(14):
            self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                               requestuser=testuser)

    def test_querycount_anonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL,
                              fullname='testuser')
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        for number in range(30):
            group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
            mommy.make('core.Examiner',
                       relatedexaminer__user=testuser,
                       assignmentgroup=group)
            mommy.make('core.Examiner',
                       relatedexaminer__user__fullname='examiner{}'.format(number),
                       assignmentgroup=group)
            mommy.make('core.Candidate',
                       relatedstudent__user__fullname='candidate{}'.format(number),
                       assignment_group=group)
        with self.assertNumQueries(14):
            self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                               requestuser=testuser)

    def test_querycount_points_to_grade_mapper_custom_table(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL,
                              fullname='testuser')
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE)
        point_to_grade_map = mommy.make('core.PointToGradeMap',
                                        assignment=testassignment, invalid=False)
        mommy.make('core.PointRangeToGrade',
                   point_to_grade_map=point_to_grade_map,
                   minimum_points=0,
                   maximum_points=10,
                   grade='Bad')
        mommy.make('core.PointRangeToGrade',
                   point_to_grade_map=point_to_grade_map,
                   minimum_points=11,
                   maximum_points=70,
                   grade='Ok')
        mommy.make('core.PointRangeToGrade',
                   point_to_grade_map=point_to_grade_map,
                   minimum_points=71,
                   maximum_points=100,
                   grade='Best')
        for number in range(30):
            group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
            mommy.make('core.Examiner',
                       relatedexaminer__user=testuser,
                       assignmentgroup=group)
            mommy.make('core.Candidate',
                       relatedstudent__user__fullname='candidate{}'.format(number),
                       assignment_group=group)
            devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=group, grading_points=3)
        prefetched_assignment = Assignment.objects.prefetch_point_to_grade_map().get(id=testassignment.id)
        with self.assertNumQueries(14):
            self.mock_http200_getrequest_htmls(cradmin_role=prefetched_assignment,
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

        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=3)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup2, grading_points=10)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
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

        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=3)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup2, grading_points=10)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
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
                   feedback_set=testgroup1.feedbackset_set.first(),
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=datetime(2011, 12, 24, 0, 0))

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=testgroup2.feedbackset_set.first(),
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
                   feedback_set=testgroup1.feedbackset_set.first(),
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=datetime(2011, 12, 24, 0, 0))

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=testgroup2.feedbackset_set.first(),
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
                   feedback_set=testgroup1.feedbackset_set.first(),
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=datetime(2011, 12, 24, 0, 0))

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=testgroup2.feedbackset_set.first(),
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
                   feedback_set=testgroup1.feedbackset_set.first(),
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   published_datetime=datetime(2011, 12, 24, 0, 0))

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=testgroup2.feedbackset_set.first(),
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

    def test_filter_status_all(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser)
        self.assertEqual(
            {'user1', 'user2'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_status_waiting_for_feedback(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                first_deadline=timezone.now() - timedelta(days=2))

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=1)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup2)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'status-waiting-for-feedback'},
            requestuser=testuser)
        self.assertEqual(
            {'user2'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_status_waiting_for_feedback_new_attempt_also_waiting_for_feedback(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                first_deadline=timezone.now() - timedelta(days=2))

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup1, grading_points=1)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup2)
        devilry_group_mommy_factories.feedbackset_new_attempt_unpublished(
            group=testgroup2,
            deadline_datetime=timezone.now() - timedelta(days=1))

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'status-waiting-for-feedback'},
            requestuser=testuser)
        self.assertEqual(
            {'user1', 'user2'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_status_waiting_for_deliveries(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                first_deadline=timezone.now() + timedelta(days=2))

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=1)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup2)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'status-waiting-for-deliveries'},
            requestuser=testuser)
        self.assertEqual(
            {'user2'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_status_waiting_for_deliveries_new_attempt_also_waiting_for_deliveries(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                first_deadline=timezone.now() + timedelta(days=2))

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup1)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup2, grading_points=1)
        devilry_group_mommy_factories.feedbackset_new_attempt_unpublished(
            group=testgroup2,
            deadline_datetime=timezone.now() + timedelta(days=3))

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'status-waiting-for-deliveries'},
            requestuser=testuser)
        self.assertEqual(
            {'user1', 'user2'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_status_corrected(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=1)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup2)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'status-corrected'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_status_corrected_new_attempt_corrected(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=1)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup2)
        devilry_group_mommy_factories.feedbackset_new_attempt_published(
            group=testgroup2)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'status-corrected'},
            requestuser=testuser)
        self.assertEqual(
            {'user1', 'user2'},
            set(self.__get_titles(mockresponse.selector)))

    def test_render_status_all_label(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup2)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup3)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser)
        self.assertEqual(
            'all students 3',
            mockresponse.selector.one(
                '#django_cradmin_listfilter_status_input__label').alltext_normalized)

    def test_render_status_waiting_for_feedback_label(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                first_deadline=timezone.now() - timedelta(days=2))

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup2)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup3)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup3)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser)
        self.assertEqual(
            'waiting for feedback 2',
            mockresponse.selector.one(
                '#django_cradmin_listfilter_status_input_waiting-for-feedback_label').alltext_normalized)

    def test_render_status_waiting_for_feedback_label_with_new_attempt(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            first_deadline=timezone.now() - timedelta(days=2))

        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        devilry_group_mommy_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=timezone.now() - timedelta(days=1))

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser)
        self.assertEqual(
            'waiting for feedback 1',
            mockresponse.selector.one(
                '#django_cradmin_listfilter_status_input_waiting-for-feedback_label').alltext_normalized)

    def test_render_status_waiting_for_deliveries_label(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                first_deadline=timezone.now() + timedelta(days=2))

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup2)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup3)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup3, grading_points=1)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser)
        self.assertEqual(
            'waiting for deliveries 2',
            mockresponse.selector.one(
                '#django_cradmin_listfilter_status_input_waiting-for-deliveries_label').alltext_normalized)

    def test_render_status_waiting_for_deliveries_label_with_new_attempt(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start')

        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup)
        devilry_group_mommy_factories.feedbackset_new_attempt_unpublished(
            group=testgroup,
            deadline_datetime=timezone.now() + timezone.timedelta(days=1))

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser)
        self.assertEqual(
            'waiting for deliveries 1',
            mockresponse.selector.one(
                '#django_cradmin_listfilter_status_input_waiting-for-deliveries_label').alltext_normalized)

    def test_render_status_corrected_label(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                first_deadline=timezone.now() - timedelta(days=2))

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup2)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup3)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup3)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser)
        self.assertEqual(
            'corrected 2',
            mockresponse.selector.one(
                '#django_cradmin_listfilter_status_input_corrected_label').alltext_normalized)

    def test_filter_is_passing_grade_true(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            passing_grade_min_points=1)

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=0)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup2)

        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup3, grading_points=1)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'is_passing_grade-true'},
            requestuser=testuser)
        self.assertEqual(
            {'user3'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_is_passing_grade_false(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            passing_grade_min_points=1)

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=0)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup2)

        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup3, grading_points=1)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'is_passing_grade-false'},
            requestuser=testuser)
        self.assertEqual(
            {'user1', 'user2'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_points_zero(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=0)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup2)

        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup3, grading_points=10)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'points-0'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_points_nonzero(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=0)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup2)

        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup3, grading_points=10)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'points-10'},
            requestuser=testuser)
        self.assertEqual(
            {'user3'},
            set(self.__get_titles(mockresponse.selector)))

    def test_render_examiner_filter_if_multiple_examiners(self):
        testuser1 = mommy.make(settings.AUTH_USER_MODEL)
        testuser2 = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        relatedexaminer1 = mommy.make('core.RelatedExaminer', user=testuser1)
        relatedexaminer2 = mommy.make('core.RelatedExaminer', user=testuser2)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer=relatedexaminer1)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer=relatedexaminer2)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser1)
        self.assertTrue(mockresponse.selector.exists('#django_cradmin_listfilter_examiner_input'))

    def test_do_not_render_examiner_filter_if_single_examiner(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        relatedexaminer = mommy.make('core.RelatedExaminer', user=testuser)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer=relatedexaminer)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser)
        self.assertFalse(mockresponse.selector.exists('#django_cradmin_listfilter_examiner_input'))

    def test_render_examiner_filter_choices(self):
        testuser1 = mommy.make(settings.AUTH_USER_MODEL, fullname='A')
        testuser2 = mommy.make(settings.AUTH_USER_MODEL, shortname='c')
        testuser3 = mommy.make(settings.AUTH_USER_MODEL, fullname='B')
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        relatedexaminer1 = mommy.make('core.RelatedExaminer', user=testuser1)
        relatedexaminer2 = mommy.make('core.RelatedExaminer', user=testuser2)
        relatedexaminer3 = mommy.make('core.RelatedExaminer', user=testuser3)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer=relatedexaminer1)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer=relatedexaminer2)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer=relatedexaminer3)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser1)
        choices_labels = [
            element.alltext_normalized
            for element in mockresponse.selector.list('#django_cradmin_listfilter_examiner_input option')]
        self.assertEqual(
            ['', 'A', 'B', 'c'],
            choices_labels)

    def test_filter_examiner(self):
        testuser1 = mommy.make(settings.AUTH_USER_MODEL)
        testuser2 = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        relatedexaminer1 = mommy.make('core.RelatedExaminer', user=testuser1)
        relatedexaminer2 = mommy.make('core.RelatedExaminer', user=testuser2)

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer=relatedexaminer1)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer=relatedexaminer2)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer=relatedexaminer1)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'examiner-{}'.format(relatedexaminer2.id)},
            requestuser=testuser1)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_studentfile(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        comment = mommy.make(
            'devilry_group.GroupComment',
            feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
            comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
            user_role=Comment.USER_ROLE_STUDENT,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_comment.CommentFile', comment=comment)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'activity-studentfile'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_no_studentfile(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        comment = mommy.make(
            'devilry_group.GroupComment',
            feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
            comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
            user_role=Comment.USER_ROLE_STUDENT,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_comment.CommentFile', comment=comment)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'activity-no-studentfile'},
            requestuser=testuser)
        self.assertEqual(
            {'user2'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_studentcomment_groupcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'activity-studentcomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_studentcomment_imageannotationcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'activity-studentcomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_no_studentcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup2),
                   comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'activity-no-studentcomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user3'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_examinercomment_groupcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'activity-examinercomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_examinercomment_imageannotationcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'activity-examinercomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_no_examinercomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup2),
                   comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup3, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'activity-no-examinercomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user3'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_admincomment_groupcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   user_role=Comment.USER_ROLE_ADMIN,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'activity-admincomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_admincomment_imageannotationcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
                   user_role=Comment.USER_ROLE_ADMIN,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'activity-admincomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_unpublishedfeedback(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup1, grading_points=1),

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup2),

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'activity-unpublishedfeedback'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_private_comment_groupcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   user=testuser,
                   visibility=GroupComment.VISIBILITY_PRIVATE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'activity-privatecomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_private_comment_imageannotationcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   user=testuser,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup2, relatedexaminer__user=testuser)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'activity-privatecomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_no_result_message(self):
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
            'No students found matching your filters/search.',
            mockresponse.selector.one('.django-cradmin-listing-no-items-message').alltext_normalized)

    def test_filter_waiting_for_feedback_empty(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            first_deadline=ACTIVE_PERIOD_END)

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'status-waiting-for-feedback'},
            requestuser=testuser)
        self.assertEqual(
            'You have no students waiting for feedback.',
            mockresponse.selector.one('.devilry-examiner-grouplist-empty').alltext_normalized)
        self.assertTrue(
            mockresponse.selector.one('.devilry-examiner-grouplist-empty').hasclass(
                'devilry-examiner-grouplist-empty-waiting-for-feedback'))

    def test_filter_waiting_for_deliveries_empty(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            first_deadline=ACTIVE_PERIOD_START)

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'status-waiting-for-deliveries'},
            requestuser=testuser)
        self.assertEqual(
            'You are currently not expecting new deliveries from any students.',
            mockresponse.selector.one('.devilry-examiner-grouplist-empty').alltext_normalized)
        self.assertTrue(
            mockresponse.selector.one('.devilry-examiner-grouplist-empty').hasclass(
                'devilry-examiner-grouplist-empty-waiting-for-deliveries'))

    def test_filter_corrected_empty(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup1, relatedexaminer__user=testuser)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'status-corrected'},
            requestuser=testuser)
        self.assertEqual(
            'You have not finished correcting any students yet.',
            mockresponse.selector.one('.devilry-examiner-grouplist-empty').alltext_normalized)
        self.assertTrue(
            mockresponse.selector.one('.devilry-examiner-grouplist-empty').hasclass(
                'devilry-examiner-grouplist-empty-corrected'))

    def test_bulk_feedback_choices_not_rendered_no_groups_waiting_for_feedback(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start'))
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup.parentnode,
            requestuser=testuser
        )
        self.assertFalse(mockresponse.selector.exists('#devilry-examiner-bulk-feedback-button'))
        self.assertFalse(mockresponse.selector.exists('#devilry-examiner-simple-bulk-feedback-button'))

    def test_bulk_feedback_choices_rendered_group_waiting_for_feedback(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   first_deadline=timezone.now() - timezone.timedelta(days=1)))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup.parentnode,
            requestuser=testuser
        )
        self.assertTrue(mockresponse.selector.exists('#devilry-examiner-bulk-feedback-button'))
        self.assertTrue(mockresponse.selector.exists('#devilry-examiner-simple-bulk-feedback-button'))

    def test_bulk_feedback_button_text(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   first_deadline=timezone.now() - timezone.timedelta(days=1)))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup.parentnode,
            requestuser=testuser
        )
        self.assertEquals(
            'Bulk feedback',
            mockresponse.selector.one('#devilry-examiner-bulk-feedback-button').alltext_normalized)

    def test_simple_bulk_feedback_button_text(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   first_deadline=timezone.now() - timezone.timedelta(days=1)))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup.parentnode,
            requestuser=testuser
        )
        self.assertEquals(
            'Simple bulk feedback',
            mockresponse.selector.one('#devilry-examiner-simple-bulk-feedback-button').alltext_normalized)

    def test_new_attempt_box_rendered_button_text(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(group=testgroup2)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup1)
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            requestuser=testuser
        )
        self.assertEquals(
            'Manage deadlines',
            mockresponse.selector.one('#devilry-examiner-bulk-new-attempt-button').alltext_normalized)
