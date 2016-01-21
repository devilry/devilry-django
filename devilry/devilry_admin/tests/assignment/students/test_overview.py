from django import test
from django.conf import settings
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_admin.views.assignment.students import overview


class TestOverview(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    NOTE: Most of the functionality for this view is tested in
    devilry.devilry_admin.tests.assignment.students.test_groupview_base.test_groupviewmixin.TestGroupViewMixin
    and
    devilry.devilry_admin.tests.assignment.students.test_groupview_base.test_baseinforview.TestBaseInfoView
    """
    viewclass = overview.Overview

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

    def test_filter_all_empty(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')

        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            'You have no students for this assignment. Add students using the link above.',
            mockresponse.selector.one('.devilry-admin-grouplist-empty').alltext_normalized)
        self.assertTrue(
            mockresponse.selector.one('.devilry-admin-grouplist-empty').hasclass(
                'devilry-admin-grouplist-empty-all'))

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
