from __future__ import unicode_literals
from datetime import timedelta

from django import test
from django.conf import settings
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url
from model_mommy import mommy

from devilry.apps.core.models import Assignment
from devilry.apps.core.mommy_recipes import ACTIVE_PERIOD_START
from devilry.devilry_comment.models import Comment
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group.models import GroupComment
from devilry.devilry_student.views.dashboard import dashboard


class TestDashboardView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = dashboard.DashboardView

    def test_title(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', relatedstudent__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertIn(
                'Student dashboard',
                mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', relatedstudent__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                'Student dashboard',
                mockresponse.selector.one('h1').alltext_normalized)

    def test_page_subheader(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', relatedstudent__user=testuser)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                'Welcome! Please select an assignment below to add deliveries, '
                'view feedback or communicate with you examiner.',
                mockresponse.selector.one('.devilry-page-subheader').alltext_normalized)

    def __get_assignment_count(self, selector):
        return selector.count('.devilry-cradmin-groupitemvalue')

    def test_not_assignments_where_not_student(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                0,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_not_future_periods(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe('devilry.apps.core.assignment_futureperiod_start'))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                0,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_not_old_periods(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe('devilry.apps.core.assignment_oldperiod_end'))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                0,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_include_active_periods(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate', relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_no_active_assignments_message(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=testuser)
        self.assertEqual(
                'You have no active assignments. Use the button below to browse '
                'inactive assignments and courses',
                mockresponse.selector.one('.django-cradmin-listing-no-items-message').alltext_normalized)

    def test_assignment_url(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testcandidate = mommy.make('core.Candidate', relatedstudent__user=testuser,
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
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start'))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-nomatch'},
                requestuser=testuser)
        self.assertEqual(
                0,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_subject_short_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode__parentnode__short_name='testsubject'))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-testsubject'},
                requestuser=testuser)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_subject_long_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode__parentnode__long_name='Testsubject'))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-Testsubject'},
                requestuser=testuser)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_period_short_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode__short_name='testperiod'))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-testperiod'},
                requestuser=testuser)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_period_long_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           parentnode__long_name='Testperiod'))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-Testperiod'},
                requestuser=testuser)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_assignment_short_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe(
                           'devilry.apps.core.assignment_activeperiod_start',
                           short_name='testassignment'))
        mockresponse = self.mock_http200_getrequest_htmls(
                viewkwargs={'filters_string': 'search-testassignment'},
                requestuser=testuser)
        self.assertEqual(
                1,
                self.__get_assignment_count(selector=mockresponse.selector))

    def test_grouplist_search_match_assignment_long_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group__parentnode=mommy.make_recipe(
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
                requestuser=testuser)
        self.assertEqual(
                [
                    'testsubject1.testperiod - Assignment 2',
                    'testsubject2.testperiod - Assignment 1',
                    'testsubject1.testperiod - Assignment 1',
                ],
                self.__get_assignment_titles(mockresponse.selector))

    def test_grouplist_title_sanity(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                       'devilry.apps.core.assignment_activeperiod_start',
                                       parentnode__parentnode__short_name='testsubject',
                                       parentnode__short_name='testperiod',
                                       long_name='Test Assignment'))
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser)
        self.assertEqual(
            'testsubject.testperiod - Test Assignment',
            mockresponse.selector.one(
                    '.devilry-cradmin-groupitemvalue '
                    '.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized
        )

    def test_grouplist_no_examiners(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        mommy.make('core.Examiner',
                   assignmentgroup=testgroup)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser)
        self.assertTrue(
            mockresponse.selector.exists('.devilry-cradmin-groupitemvalue'))
        self.assertFalse(
            mockresponse.selector.exists('.devilry-cradmin-groupitemvalue-examiners'))

    def test_grouplist_status_waiting_for_deliveries_sanity(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=3, is_last_in_group=False)
        devilry_group_mommy_factories.feedbackset_new_attempt_unpublished(
            group=testgroup, is_last_in_group=True,
            deadline_datetime=timezone.now() + timedelta(days=2))
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser)
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
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=3, is_last_in_group=False)
        devilry_group_mommy_factories.feedbackset_new_attempt_unpublished(
            group=testgroup, is_last_in_group=True,
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
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=3, is_last_in_group=False)
        devilry_group_mommy_factories.feedbackset_new_attempt_published(
            group=testgroup, is_last_in_group=True, grading_points=2)
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
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start'))
        mommy.make('core.Candidate',
                   relatedstudent__user=testuser,
                   assignment_group=testgroup)
        feedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup)
        mommy.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user_role=Comment.USER_ROLE_STUDENT,
                   _quantity=2)
        mommy.make('devilry_comment.CommentFile',
                   comment=mommy.make('devilry_group.GroupComment',
                                      feedback_set=feedbackset,
                                      visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                                      user_role=Comment.USER_ROLE_STUDENT))
        mommy.make('devilry_group.GroupComment',
                   feedback_set=feedbackset,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE,
                   user_role=Comment.USER_ROLE_EXAMINER,
                   _quantity=5)
        mommy.make('devilry_group.GroupComment',  # Should not be part of count
                   feedback_set=feedbackset,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS,
                   user_role=Comment.USER_ROLE_EXAMINER)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=testuser)
        self.assertEqual(
                '3 comments from student. 1 file from student. 5 comments from examiner.',
                mockresponse.selector.one(
                        '.devilry-cradmin-groupitemvalue '
                        '.devilry-cradmin-groupitemvalue-comments').alltext_normalized)

    def test_querycount(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        for number in range(30):
            group = mommy.make('core.AssignmentGroup', parentnode=testassignment)
            mommy.make('core.Examiner',
                       assignmentgroup=group)
            mommy.make('core.Candidate',
                       relatedstudent__user=testuser,
                       assignment_group=group)
            devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=group, grading_points=1)
        with self.assertNumQueries(1):
            self.mock_http200_getrequest_htmls(requestuser=testuser)

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
                       assignmentgroup=group)
            mommy.make('core.Candidate',
                       relatedstudent__user__fullname='candidate{}'.format(number),
                       assignment_group=group)
            devilry_group_mommy_factories.feedbackset_first_attempt_published(
                group=group, grading_points=3)
        with self.assertNumQueries(1):
            self.mock_http200_getrequest_htmls(requestuser=testuser)
