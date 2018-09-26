from datetime import datetime, timedelta

import mock
from django import test
from django.conf import settings
from django.utils import timezone
from django_cradmin import cradmin_testhelpers
from django_cradmin.viewhelpers import listbuilder
from django_cradmin.viewhelpers import listbuilderview
from model_mommy import mommy

from devilry.apps.core import devilry_core_mommy_factories
from devilry.apps.core.models import Assignment
from devilry.devilry_admin.views.assignment.students import groupview_base
from devilry.devilry_comment.models import Comment
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group.models import GroupComment, ImageAnnotationComment
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class MinimalGroupItemValue(listbuilder.itemvalue.TitleDescription):
    valuealias = 'group'

    def get_title(self):
        # Since we only test with single candidates in the group
        # in TestGroupViewMixin, we only need the name of the first candidate
        candidates = list(self.group.candidates.all())
        if candidates:
            return candidates[0].relatedstudent.user.shortname
        else:
            return 'No candidates'


class MinimalGroupViewMixin(groupview_base.GroupViewMixin,
                            listbuilderview.FilterListMixin,
                            listbuilderview.View):
    value_renderer_class = MinimalGroupItemValue


class TestGroupViewMixin(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = MinimalGroupViewMixin

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

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
            ['b', 'a'],
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
            ['a', 'b'],
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

        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=3)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup2, grading_points=10)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
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

        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=3)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup2, grading_points=10)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
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
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=1)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
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
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=1)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
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
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=1)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup2)

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'status-corrected'},
            requestuser=testuser)
        self.assertEqual(
            {'user1'},
            set(self.__get_titles(mockresponse.selector)))

    def test_filter_is_passing_grade_true(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            passing_grade_min_points=1)

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=0)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup2)

        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
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
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=0)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup2)

        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
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
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=0)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup2)

        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
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
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup1, grading_points=0)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup2)

        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup3, shortname='user3')
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
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
        AssignmentGroupDbCacheCustomSql().initialize()
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        comment = mommy.make(
            'devilry_group.GroupComment',
            feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
            comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
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
        AssignmentGroupDbCacheCustomSql().initialize()
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        comment = mommy.make(
            'devilry_group.GroupComment',
            feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
            comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
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
        AssignmentGroupDbCacheCustomSql().initialize()
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   text='asd',
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
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
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
        AssignmentGroupDbCacheCustomSql().initialize()
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   text='asd',
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup2),
                   comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
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
        AssignmentGroupDbCacheCustomSql().initialize()
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
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
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
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
        AssignmentGroupDbCacheCustomSql().initialize()
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup2),
                   comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
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
        AssignmentGroupDbCacheCustomSql().initialize()
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup1, shortname='user1')
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   comment_type=GroupComment.COMMENT_TYPE_GROUPCOMMENT,
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
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
                   comment_type=ImageAnnotationComment.COMMENT_TYPE_IMAGEANNOTATION,
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
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
            group=testgroup1, grading_points=1),

        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_core_mommy_factories.candidate(group=testgroup2, shortname='user2')
        devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(
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
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
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
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup1),
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
            ['b', 'a'],
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
            ['a', 'b'],
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
            ['b', 'a'],
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
            ['a', 'b'],
            self.__get_titles(mockresponse.selector))

    def test_examiner_count_2(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='a',
                   relatedstudent__user__fullname='A')
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__user__shortname='b',
                   relatedstudent__user__fullname='B')
        devilry_core_mommy_factories.examiner(group=testgroup1)
        devilry_core_mommy_factories.examiner(group=testgroup1)
        devilry_core_mommy_factories.examiner(group=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'examinercount-eq-2'},
            requestuser=testuser)
        self.assertEqual(
            ['a'],
            self.__get_titles(mockresponse.selector))

    def test_examiner_count_2_and_candidates_count_2(self):
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
                   assignment_group=testgroup1)
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__user__shortname='a',
                   relatedstudent__user__fullname='B')
        devilry_core_mommy_factories.examiner(group=testgroup1)
        devilry_core_mommy_factories.examiner(group=testgroup2)
        devilry_core_mommy_factories.examiner(group=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'examinercount-eq-2'},
            requestuser=testuser)
        self.assertEqual(
            ['a'],
            self.__get_titles(mockresponse.selector))

    def test_examiner_count_5(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='b',
                   relatedstudent__user__fullname='A')
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__user__shortname='a',
                   relatedstudent__user__fullname='B')
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__user__shortname='c',
                   relatedstudent__user__fullname='C')
        for index in range(5):
            devilry_core_mommy_factories.examiner(group=testgroup1)
            devilry_core_mommy_factories.examiner(group=testgroup2)
        devilry_core_mommy_factories.examiner(group=testgroup3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'examinercount-eq-5'},
            requestuser=testuser)
        self.assertEqual(
            ['b', 'a'],
            self.__get_titles(mockresponse.selector))

    def test_examiner_count_filter_not_found(self):
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
        devilry_core_mommy_factories.examiner(group=testgroup1)
        devilry_core_mommy_factories.examiner(group=testgroup2)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'examinercount-eq-2'},
            requestuser=testuser)
        self.assertEqual(
            [],
            self.__get_titles(mockresponse.selector))

    def test_candidate_count_filter_1(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='b',
                   relatedstudent__user__fullname='A')
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__user__shortname='a',
                   relatedstudent__user__fullname='B')
        mommy.make('core.Candidate',
                   assignment_group=testgroup3,
                   _quantity=3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'candidatecount-eq-1'},
            requestuser=testuser)
        self.assertEqual(
            ['b', 'a'],
            self.__get_titles(mockresponse.selector))

    def test_candidate_count_filter_4(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='b',
                   relatedstudent__user__fullname='A')
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__user__shortname='a',
                   relatedstudent__user__fullname='B')
        for index in range(3):

            mommy.make('core.Candidate',
                       assignment_group=testgroup1,
                       relatedstudent__user__shortname='Q{}'.format(index),
                       relatedstudent__user__fullname='Q{}'.format(index))

            mommy.make('core.Candidate',
                       assignment_group=testgroup2,
                       relatedstudent__user__shortname='P{}'.format(index),
                       relatedstudent__user__fullname='P{}'.format(index))
        mommy.make('core.Candidate',
                   assignment_group=testgroup3,
                   _quantity=7)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'candidatecount-eq-4'},
            requestuser=testuser)
        self.assertEqual(
            ['b', 'a'],
            self.__get_titles(mockresponse.selector))

    def test_candidate_count_filter_not_found(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup3 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('core.Candidate',
                   assignment_group=testgroup1,
                   relatedstudent__user__shortname='b',
                   relatedstudent__user__fullname='A')
        mommy.make('core.Candidate',
                   assignment_group=testgroup2,
                   relatedstudent__user__shortname='a',
                   relatedstudent__user__fullname='B')
        mommy.make('core.Candidate',
                   assignment_group=testgroup3,
                   _quantity=3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            viewkwargs={'filters_string': 'candidatecount-eq-2'},
            requestuser=testuser)
        self.assertEqual(
            [],
            self.__get_titles(mockresponse.selector))
