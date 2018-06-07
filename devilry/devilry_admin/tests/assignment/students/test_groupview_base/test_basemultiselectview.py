from datetime import timedelta

import mock
from django import test
from django.conf import settings
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core.models import Assignment
from devilry.devilry_admin.views.assignment.students import groupview_base
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories


class MinimalMultiselectView(groupview_base.BaseMultiselectView):
    filterview_name = 'filter'


class TestBaseMultiselectView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    NOTE: Most of the functionality for this view is tested in
    devilry.devilry_admin.tests.assignment.students.test_groupview_base.test_groupviewmixin.TestGroupViewMixin
    """
    viewclass = MinimalMultiselectView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_filter_no_result_message(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start'))
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testuser')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
                viewkwargs={'filters_string': 'search-nomatch'},
                requestuser=testuser)
        self.assertEqual(
            'No students found matching your filters/search.',
            mockresponse.selector.one('.django-cradmin-listing-no-items-message').alltext_normalized)

    def test_filter_all_empty(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            'No students.',
            mockresponse.selector.one('.django-cradmin-listing-no-items-message').alltext_normalized)

    def test_group_render_title_name_order(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='userb')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='usera')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            'usera , userb',
            mockresponse.selector.one(
                '.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_group_render_title_name_order_fullname(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
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
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            'A user(userc) , usera , userb',
            mockresponse.selector.one(
                '.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)


    #
    #
    # Anonymization tests
    #
    #

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
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup.assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
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
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup.assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            requestuser=testuser)
        self.assertIn('unanonymizedfullname', mockresponse.response.content)
        self.assertIn('A un-anonymized fullname', mockresponse.response.content)
        self.assertNotIn('MyAnonymousID', mockresponse.response.content)

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
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testgroup.assignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            requestuser=testuser)
        self.assertIn('unanonymizedfullname', mockresponse.response.content)
        self.assertIn('A un-anonymized fullname', mockresponse.response.content)
        self.assertNotIn('MyAnonymousID', mockresponse.response.content)

    def test_anonymizationmode_fully_anonymous_subjectadmin_no_examiners(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
                requestuser=testuser)
        self.assertFalse(mockresponse.selector.exists('.devilry-cradmin-groupitemvalue-examiners'))

    def test_anonymizationmode_fully_anonymous_departmentadmin_has_examiners(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS))
        mommy.make('core.Examiner',
                   relatedexaminer__user=testuser,
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
                requestuser=testuser)
        self.assertTrue(mockresponse.selector.exists('.devilry-cradmin-groupitemvalue-examiners'))

    def test_anonymizationmode_fully_anonymous_subjectadmin_no_status(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
                requestuser=testuser)
        self.assertFalse(mockresponse.selector.exists('.devilry-cradmin-groupitemvalue-status'))

    def test_anonymizationmode_fully_anonymous_departmentadmin_has_status(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
                requestuser=testuser)
        self.assertTrue(mockresponse.selector.exists('.devilry-cradmin-groupitemvalue-status'))

    def test_anonymizationmode_fully_anonymous_subjectadmin_no_grade(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS))
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=3)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
                requestuser=testuser)
        self.assertFalse(mockresponse.selector.exists('.devilry-cradmin-groupitemvalue-grade'))

    def test_anonymizationmode_fully_anonymous_departmentadmin_has_grade(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS))
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=3)
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
                requestuser=testuser)
        self.assertTrue(mockresponse.selector.exists('.devilry-cradmin-groupitemvalue-grade'))

    def test_anonymizationmode_fully_anonymous_subjectadmin_no_comments(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
                requestuser=testuser)
        self.assertFalse(mockresponse.selector.exists('.devilry-cradmin-groupitemvalue-comments'))

    def test_anonymizationmode_fully_anonymous_departmentadmin_has_comments(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
                requestuser=testuser)
        self.assertTrue(mockresponse.selector.exists('.devilry-cradmin-groupitemvalue-comments'))

    #
    #
    # Querycount tests
    #
    #

    def test_querycount(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL,
                              fullname='testuser')
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        for number in range(30):
            group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
            mommy.make('core.Examiner',
                       relatedexaminer__user=testuser,
                       assignmentgroup=group)
            mommy.make('core.Candidate',
                       relatedstudent__user__fullname='candidate{}'.format(number),
                       assignment_group=group)
        with self.assertNumQueries(10):
            self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                               cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
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
        with self.assertNumQueries(11):
            self.mock_http200_getrequest_htmls(cradmin_role=prefetched_assignment,
                                               cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
                                               requestuser=testuser)

    def test_querycount_fully_anonymous(self):
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
            mommy.make('core.Candidate',
                       relatedstudent__user__fullname='candidate{}'.format(number),
                       assignment_group=group)
        with self.assertNumQueries(10):
            self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                               cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
                                               requestuser=testuser)
