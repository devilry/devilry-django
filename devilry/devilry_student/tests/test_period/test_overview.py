

from datetime import timedelta

from django import test
from django.conf import settings
from django.utils import timezone
from cradmin_legacy import cradmin_testhelpers
from cradmin_legacy import crapp
from cradmin_legacy.crinstance import reverse_cradmin_url
from model_bakery import baker

from devilry.apps.core.models import Assignment
from devilry.apps.core.baker_recipes import ACTIVE_PERIOD_START
from devilry.devilry_comment.models import Comment
from devilry.devilry_group import devilry_group_baker_factories
from devilry.devilry_group.models import GroupComment
from devilry.devilry_student.views.period import overview
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestPeriodOverviewView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.PeriodOverviewView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_title(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active',
                                       parentnode__long_name='Test Subject',
                                       long_name='Test Period')
        baker.make('core.Candidate', relatedstudent__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser, cradmin_role=testperiod)
        self.assertIn(
                'Test Subject - Test Period',
                mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active',
                                       parentnode__long_name='Test Subject',
                                       long_name='Test Period')
        baker.make('core.Candidate', relatedstudent__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                'Test Subject - Test Period',
                mockresponse.selector.one('h1').alltext_normalized)

    def __get_assignment_count(self, selector):
        return selector.count('.devilry-cradmin-groupitemvalue')

    def test_not_assignments_where_not_student(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                0,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_not_future_periods(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_future')
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_futureperiod_start',
                           parentnode=testperiod))
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                0,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_include_old_periods(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_old')
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_oldperiod_end',
                           parentnode=testperiod))
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_include_active_periods(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.Candidate', relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode=testperiod))
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_no_active_assignments_message(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                'No assignments.',
                mockresponse.selector.one('.cradmin-legacy-listing-no-items-message').alltext_normalized)

    def test_assignment_url(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        testassignment = baker.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                parentnode=testperiod)
        testcandidate = baker.make('core.Candidate', relatedstudent__user=testuser,
                                   assignment_group__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser, cradmin_role=testperiod)
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
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode=testperiod))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-nomatch'},
                requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                0,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_subject_short_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active',
                                       parentnode__short_name='testsubject')
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode=testperiod))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-testsubject'},
                requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_subject_long_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active',
                                       parentnode__long_name='Testsubject')
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode=testperiod))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-Testsubject'},
                requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_period_short_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active',
                                       short_name='testperiod')
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode=testperiod))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-testperiod'},
                requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_period_long_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active',
                                       long_name='Testperiod')
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode=testperiod))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-Testperiod'},
                requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_assignment_short_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           short_name='testassignment',
                           parentnode=testperiod))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-testassignment'},
                requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_assignment_long_name(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           long_name='Testassignment',
                           parentnode=testperiod))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-Testassignment'},
                requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def __get_assignment_titles(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.devilry-cradmin-groupitemvalue '
                                             '.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]

    def test_grouplist_orderby(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           long_name='Assignment 1',
                           first_deadline=ACTIVE_PERIOD_START + timedelta(days=1),
                           parentnode=testperiod))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           long_name='Assignment 3',
                           first_deadline=ACTIVE_PERIOD_START + timedelta(days=3),
                           parentnode=testperiod))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=baker.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           long_name='Assignment 2',
                           first_deadline=ACTIVE_PERIOD_START + timedelta(days=2),
                           parentnode=testperiod))
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                [
                    'Assignment 3',
                    'Assignment 2',
                    'Assignment 1',
                ],
                self.__get_assignment_titles(mockresponse.selector))

    def test_grouplist_title_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe(
                                       'devilry.apps.core.assignment_activeperiod_start',
                                       parentnode=testperiod,
                                       long_name='Test Assignment'))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                'Test Assignment',
                mockresponse.selector.one(
                        '.devilry-cradmin-groupitemvalue '
                        '.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized
        )

    def test_grouplist_no_examiners(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                            parentnode=testperiod))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        baker.make('core.Examiner',
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser, cradmin_role=testperiod)
        self.assertTrue(
                mockresponse.selector.exists('.devilry-cradmin-groupitemvalue'))
        self.assertFalse(
                mockresponse.selector.exists('.devilry-cradmin-groupitemvalue-examiners'))

    def test_grouplist_status_waiting_for_deliveries_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                            parentnode=testperiod))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
                group=testgroup, grading_points=3)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
                group=testgroup,
                deadline_datetime=timezone.now() + timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser, cradmin_role=testperiod)
        self.assertFalse(
                mockresponse.selector.exists(
                        '.devilry-cradmin-groupitemvalue '
                        '.devilry-cradmin-groupitemvalue-grade'))
        self.assertEqual(
                'Status: waiting for deliveries',
                mockresponse.selector.one(
                        '.devilry-cradmin-groupitemvalue '
                        '.devilry-cradmin-groupitemvalue-status').alltext_normalized)

    def test_grouplist_status_waiting_for_feedback_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                            parentnode=testperiod))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
                group=testgroup, grading_points=3)
        devilry_group_baker_factories.feedbackset_new_attempt_unpublished(
                group=testgroup,
                deadline_datetime=timezone.now() - timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser, cradmin_role=testperiod)
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
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                            parentnode=testperiod))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        devilry_group_baker_factories.feedbackset_first_attempt_published(
                group=testgroup, grading_points=3)
        devilry_group_baker_factories.feedbackset_new_attempt_published(
                group=testgroup, grading_points=2)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser, cradmin_role=testperiod)
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
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                                            parentnode=testperiod))
        baker.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        feedbackset = devilry_group_baker_factories.feedbackset_first_attempt_unpublished(
                group=testgroup)
        baker.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   text='asd',
                   user_role=Comment.USER_ROLE_STUDENT,
                   _quantity=2)
        baker.make('devilry_comment.CommentFile',
                   comment=baker.make('devilry_group.GroupComment',
                                      feedback_set=feedbackset,
                                      comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                                      visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                                      user_role=Comment.USER_ROLE_STUDENT))
        baker.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user_role=Comment.USER_ROLE_EXAMINER,
                   _quantity=5)
        baker.make('devilry_group.GroupComment',  # Should not be part of count
                   feedback_set=feedbackset,
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   user_role=Comment.USER_ROLE_EXAMINER)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                '2 comments from student. 1 file from student. 5 comments from examiner.',
                mockresponse.selector.one(
                        '.devilry-cradmin-groupitemvalue '
                        '.devilry-cradmin-groupitemvalue-comments').alltext_normalized)

    def test_no_pagination(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.Candidate', relatedstudent__user=testuser,
                   assignment_group__parentnode__parentnode=testperiod,
                   _quantity=overview.PeriodOverviewView.paginate_by)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser, cradmin_role=testperiod)
        self.assertFalse(mockresponse.selector.exists('.cradmin-legacy-loadmorepager'))

    def test_pagination(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.Candidate', relatedstudent__user=testuser,
                   assignment_group__parentnode__parentnode=testperiod,
                   _quantity=overview.PeriodOverviewView.paginate_by + 1)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser, cradmin_role=testperiod)
        self.assertTrue(mockresponse.selector.exists('.cradmin-legacy-loadmorepager'))

    def test_querycount(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        testassignment1 = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                            parentnode=testperiod)
        testassignment2 = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                            parentnode=testperiod)

        loops = overview.PeriodOverviewView.paginate_by / 2
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
        with self.assertNumQueries(4):
            mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                loops * 2,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_querycount_points_to_grade_mapper_custom_table(self):
        testuser = baker.make(settings.AUTH_USER_MODEL,
                              fullname='testuser')
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        testassignment1 = baker.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE,
                parentnode=testperiod)
        point_to_grade_map1 = baker.make('core.PointToGradeMap',
                                         assignment=testassignment1, invalid=False)
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map1,
                   minimum_points=0, maximum_points=1)
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map1,
                   minimum_points=2, maximum_points=3)
        testassignment2 = baker.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE,
                parentnode=testperiod)
        point_to_grade_map2 = baker.make('core.PointToGradeMap',
                                         assignment=testassignment2, invalid=False)
        baker.make('core.PointRangeToGrade', point_to_grade_map=point_to_grade_map2,
                   minimum_points=0, maximum_points=1)

        loops = overview.PeriodOverviewView.paginate_by / 2
        for number in range(int(round(loops))):
            group1 = baker.make('core.AssignmentGroup', parentnode=testassignment1)
            baker.make('core.Candidate', relatedstudent__user=testuser, assignment_group=group1)
            devilry_group_baker_factories.feedbackset_first_attempt_published(
                    group=group1, grading_points=1)

            group2 = baker.make('core.AssignmentGroup', parentnode=testassignment2)
            baker.make('core.Candidate', relatedstudent__user=testuser, assignment_group=group2)
            devilry_group_baker_factories.feedbackset_first_attempt_published(
                    group=group2, grading_points=1)
        with self.assertNumQueries(5):
            mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser, cradmin_role=testperiod)
        self.assertEqual(
                loops * 2,
                self.__get_assignment_count(selector=mockresponse.selector))
