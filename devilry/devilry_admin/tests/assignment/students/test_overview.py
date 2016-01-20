from datetime import datetime, timedelta

import mock
from django import test
from django.conf import settings
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core import devilry_core_mommy_factories
from devilry.apps.core.models import Assignment
from devilry.devilry_admin.views.assignment.students import overview
from devilry.devilry_comment.models import Comment
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group.models import GroupComment, ImageAnnotationComment


class TestOverview(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.Overview

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_title(self):
        testassignment = mommy.make('core.Assignment', long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertIn(
            'Students on Test Assignment',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment', long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Students on Test Assignment',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_choices_sanity(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            3,
            mockresponse.selector.count(
                    '#devilry_admin_assignment_students_overview_choices li'))

    def test_choice_create_groups_link(self):
        testassignment = mommy.make('core.Assignment')
        mock_cradmin_instance = self.__mockinstance_with_devilryrole('departmentadmin')

        def mock_reverse_url(appname, viewname, **kwargs):
            return '/{}/{}'.format(appname, viewname)

        mock_cradmin_instance.reverse_url = mock_reverse_url
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=mock_cradmin_instance)
        self.assertEqual(
            '/create_groups/INDEX',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_overview_choice_create_groups a')['href'])

    def test_choice_create_groups_text(self):
        testassignment = mommy.make('core.Assignment',
                                    parentnode__short_name='testperiod',
                                    parentnode__parentnode__short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Add students',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_overview_choice_create_groups a')
            .alltext_normalized)

    def test_choice_merge_groups_link(self):
        testassignment = mommy.make('core.Assignment')
        mock_cradmin_instance = self.__mockinstance_with_devilryrole('departmentadmin')

        def mock_reverse_url(appname, viewname, **kwargs):
            return '/{}/{}'.format(appname, viewname)

        mock_cradmin_instance.reverse_url = mock_reverse_url
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=mock_cradmin_instance)
        self.assertEqual(
            # '/merge_groups/INDEX',
            '#',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_overview_choice_merge_groups a')['href'])

    def test_choice_merge_groups_text(self):
        testassignment = mommy.make('core.Assignment',
                                    parentnode__short_name='testperiod',
                                    parentnode__parentnode__short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Organize students in project groups',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_overview_choice_merge_groups a')
            .alltext_normalized)

    def test_choice_delete_groups_link(self):
        testassignment = mommy.make('core.Assignment')
        mock_cradmin_instance = self.__mockinstance_with_devilryrole('departmentadmin')

        def mock_reverse_url(appname, viewname, **kwargs):
            return '/{}/{}'.format(appname, viewname)

        mock_cradmin_instance.reverse_url = mock_reverse_url
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=mock_cradmin_instance)
        self.assertEqual(
            # '/delete_groups/INDEX',
            '#',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_overview_choice_delete_groups a')['href'])

    def test_choice_delete_groups_text(self):
        testassignment = mommy.make('core.Assignment',
                                    parentnode__short_name='testperiod',
                                    parentnode__parentnode__short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Delete students or project groups',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_overview_choice_delete_groups a')
            .alltext_normalized)

    def test_groups_sanity(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mommy.make('core.AssignmentGroup', parentnode=testassignment, _quantity=3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            3,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

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
        with self.assertNumQueries(11):
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
            devilry_group_mommy_factories.feedbackset_first_try_published(
                group=group, grading_points=3)
        with self.assertNumQueries(12):
            self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                               cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
                                               requestuser=testuser)

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

    def test_search_nomatch(self):
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
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
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
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
                viewkwargs={'filters_string': 'search-testuser'},
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
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
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
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'orderby-name_descending'},
            requestuser=testuser)
        self.assertEqual(
            ['B(a)', 'A(b)'],
            self.__get_titles(mockresponse.selector))

    def __has_orderby_option_label(self, selector, orderby_option_label):
        order_by_labels = {element.alltext_normalized
                           for element in selector.list('#django_cradmin_listfilter_orderby option')}
        return orderby_option_label in order_by_labels

    def test_orderby_shortname_ascending_rendered_emailbackend(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
                requestuser=testuser)
        self.assertTrue(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Email'))
        self.assertFalse(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Username'))

    def test_orderby_shortname_ascending_rendered_usernamebackend(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testassignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
                requestuser=testuser)
        self.assertFalse(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Email'))
        self.assertTrue(self.__has_orderby_option_label(
            selector=mockresponse.selector, orderby_option_label='Username'))

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
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'orderby-shortname_ascending'},
            requestuser=testuser)
        self.assertEqual(
            ['a', 'b'],
            self.__get_titles(mockresponse.selector))

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
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'orderby-shortname_descending'},
            requestuser=testuser)
        self.assertEqual(
            ['b', 'a'],
            self.__get_titles(mockresponse.selector))

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
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'orderby-lastname_ascending'},
            requestuser=testuser)
        self.assertEqual(
            ['user2', 'user1'],
            self.__get_titles(mockresponse.selector))

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
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
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
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')

        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup1, grading_points=3)
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup2, grading_points=10)
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup3, grading_points=2)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
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
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')

        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup1, grading_points=3)
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup2, grading_points=10)
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup3, grading_points=2)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'orderby-points_descending'},
            requestuser=testuser)
        self.assertEqual(
            ['user2', 'user1', 'user3'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_last_commented_by_student_ascending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
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

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'orderby-last_commented_by_student_ascending'},
            requestuser=testuser)
        self.assertEqual(
            ['user2', 'user1'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_last_commented_by_student_descending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
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

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'orderby-last_commented_by_student_descending'},
            requestuser=testuser)
        self.assertEqual(
            ['user1', 'user2'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_last_commented_by_examiner_ascending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
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

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'orderby-last_commented_by_examiner_ascending'},
            requestuser=testuser)
        self.assertEqual(
            ['user2', 'user1'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_last_commented_by_examiner_descending(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
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

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'orderby-last_commented_by_examiner_descending'},
            requestuser=testuser)
        self.assertEqual(
            ['user1', 'user2'],
            self.__get_titles(mockresponse.selector))

    def test_filter_status_all(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
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
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup1, grading_points=1)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group=testgroup2)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'status-waiting-for-feedback'},
            requestuser=testuser)
        self.assertEqual(
            {'user2'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_status_waiting_for_deliveries(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                first_deadline=timezone.now() + timedelta(days=2))

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup1, grading_points=1)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group=testgroup2)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'status-waiting-for-deliveries'},
            requestuser=testuser)
        self.assertEqual(
            {'user2'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_status_corrected(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup1, grading_points=1)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group=testgroup2)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'status-corrected'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_render_status_all_label(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
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
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2)
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group=testgroup2)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3)
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup3)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            'waiting for feedback 2',
            mockresponse.selector.one(
                '#django_cradmin_listfilter_status_input_waiting-for-feedback_label').alltext_normalized)

    def test_render_status_waiting_for_deliveries_label(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                first_deadline=timezone.now() + timedelta(days=2))

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2)
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group=testgroup2)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3)
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup3, grading_points=1)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            'waiting for deliveries 2',
            mockresponse.selector.one(
                '#django_cradmin_listfilter_status_input_waiting-for-deliveries_label').alltext_normalized)

    def test_render_status_corrected_label(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
                'devilry.apps.core.assignment_activeperiod_start',
                first_deadline=timezone.now() - timedelta(days=2))

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1)
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group=testgroup1)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2)
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup2)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3)
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup3)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
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
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup1, grading_points=0)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group=testgroup2)

        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup3, grading_points=1)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
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
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup1, grading_points=0)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group=testgroup2)

        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup3, grading_points=1)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'is_passing_grade-false'},
            requestuser=testuser)
        self.assertEqual(
            {'user1', 'user2'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_points_zero(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup1, grading_points=0)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group=testgroup2)

        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup3, grading_points=10)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'points-0'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_points_nonzero(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup1, grading_points=0)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group=testgroup2)

        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')
        devilry_group_mommy_factories.feedbackset_first_try_published(
            group=testgroup3, grading_points=10)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
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
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser1)
        self.assertTrue(mockresponse.selector.exists('#django_cradmin_listfilter_examiner_input'))

    def test_render_examiner_filter_if_single_examiner(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        relatedexaminer = mommy.make('core.RelatedExaminer', user=testuser)
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Examiner', assignmentgroup=testgroup, relatedexaminer=relatedexaminer)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertTrue(mockresponse.selector.exists('#django_cradmin_listfilter_examiner_input'))

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
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
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
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'examiner-{}'.format(relatedexaminer2.id)},
            requestuser=testuser1)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_studentfile(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        comment = mommy.make(
            'devilry_group.GroupComment',
            feedback_set=devilry_group_mommy_factories.feedbackset_first_try_unpublished(group=testgroup1),
            user_role=Comment.USER_ROLE_STUDENT,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_comment.CommentFile', comment=comment)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'activity-studentfile'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_no_studentfile(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        comment = mommy.make(
            'devilry_group.GroupComment',
            feedback_set=devilry_group_mommy_factories.feedbackset_first_try_unpublished(group=testgroup1),
            user_role=Comment.USER_ROLE_STUDENT,
            visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mommy.make('devilry_comment.CommentFile', comment=comment)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'activity-no-studentfile'},
            requestuser=testuser)
        self.assertEqual(
            {'user2'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_studentcomment_groupcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_try_unpublished(group=testgroup1),
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'activity-studentcomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_studentcomment_imageannotationcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_try_unpublished(group=testgroup1),
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'activity-studentcomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_no_studentcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_try_unpublished(group=testgroup1),
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_try_unpublished(group=testgroup2),
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'activity-no-studentcomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user3'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_examinercomment_groupcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_try_unpublished(group=testgroup1),
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'activity-examinercomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_examinercomment_imageannotationcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_try_unpublished(group=testgroup1),
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'activity-examinercomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_no_examinercomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_try_unpublished(group=testgroup1),
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_try_unpublished(group=testgroup2),
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'activity-no-examinercomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user3'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_admincomment_groupcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_try_unpublished(group=testgroup1),
                   user_role=Comment.USER_ROLE_ADMIN,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'activity-admincomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_admincomment_imageannotationcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_try_unpublished(group=testgroup1),
                   user_role=Comment.USER_ROLE_ADMIN,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'activity-admincomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_unpublishedfeedback(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group=testgroup1, grading_points=1),

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        devilry_group_mommy_factories.feedbackset_first_try_unpublished(
            group=testgroup2),

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'activity-unpublishedfeedback'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_private_comment_groupcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_try_unpublished(group=testgroup1),
                   user=testuser,
                   visibility=GroupComment.VISIBILITY_PRIVATE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'activity-privatecomment'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_activity_private_comment_imageannotationcomment(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_try_unpublished(group=testgroup1),
                   user=testuser,
                   visibility=ImageAnnotationComment.VISIBILITY_PRIVATE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
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
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
                viewkwargs={'filters_string': 'search-nomatch'},
                requestuser=testuser)
        self.assertEqual(
            'No students found matching your filters/search.',
            mockresponse.selector.one('.django-cradmin-listing-no-items-message').alltext_normalized)

    def test_filter_waiting_for_feedback_empty(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            first_deadline=timezone.now() - timedelta(days=2))
        mommy.make('core.AssignmentGroup', parentnode=testassignment)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
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
            first_deadline=timezone.now() + timedelta(days=2))
        mommy.make('core.AssignmentGroup', parentnode=testassignment)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
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
        mommy.make('core.AssignmentGroup', parentnode=testassignment)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'status-corrected'},
            requestuser=testuser)
        self.assertEqual(
            'Your examiners have not finished correcting any students yet.',
            mockresponse.selector.one('.devilry-examiner-grouplist-empty').alltext_normalized)
        self.assertTrue(
            mockresponse.selector.one('.devilry-examiner-grouplist-empty').hasclass(
                'devilry-examiner-grouplist-empty-corrected'))

    def test_filter_all_empty(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            'You have no students for this assignment. Add students using the link above.',
            mockresponse.selector.one('.devilry-examiner-grouplist-empty').alltext_normalized)
        self.assertTrue(
            mockresponse.selector.one('.devilry-examiner-grouplist-empty').hasclass(
                'devilry-examiner-grouplist-empty-all'))

    #
    #
    # Anonymization tests
    #
    #

    def test_anonymizationmode_semi_anonymous_periodadmin_404(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)

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
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
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
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
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
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testgroup.assignment,
                                                          cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
                                                          requestuser=testuser)
        self.assertIn('unanonymizedfullname', mockresponse.response.content)
        self.assertIn('A un-anonymized fullname', mockresponse.response.content)
        self.assertNotIn('MyAnonymousID', mockresponse.response.content)

    def test_search_anonymous_nomatch_candidate_id_from_candidate(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testgroup = mommy.make('core.AssignmentGroup',
                               parentnode=mommy.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   candidate_id='MyCandidateID')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
                viewkwargs={'filters_string': 'search-MyCandidateID'},
                requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_orderby_default_semi_anonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
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
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            ['A(b)', 'B(a)'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_name_descending_semi_anonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
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
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'orderby-name_descending'},
            requestuser=testuser)
        self.assertEqual(
            ['B(a)', 'A(b)'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_default_fully_anonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
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
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            ['A(b)', 'B(a)'],
            self.__get_titles(mockresponse.selector))

    def test_orderby_name_descending_fully_anonymous(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
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
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'orderby-name_descending'},
            requestuser=testuser)
        self.assertEqual(
            ['B(a)', 'A(b)'],
            self.__get_titles(mockresponse.selector))

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
        with self.assertNumQueries(11):
            self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                               cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
                                               requestuser=testuser)
