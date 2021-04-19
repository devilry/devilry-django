import mock
from django import test
from django.conf import settings
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.apps.core.models import Assignment
from devilry.devilry_admin.views.assignment.students import overview


class TestOverview(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    NOTE: Most of the functionality for this view is tested in
    devilry.devilry_admin.tests.assignment.students.test_groupview_base.test_groupviewmixin.TestGroupViewMixin
    and
    devilry.devilry_admin.tests.assignment.students.test_groupview_base.test_baseinforview.TestBaseInfoView
    """
    viewclass = overview.Overview

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_title(self):
        testassignment = baker.make('core.Assignment', long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertIn(
            'Students on Test Assignment',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = baker.make('core.Assignment', long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Students on Test Assignment',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_buttonbar_sanity(self):
        testassignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            4,
            mockresponse.selector.count(
                '#devilry_admin_assignment_students_overview_buttonbar .btn'))

    def test_buttonbar_create_groups_link(self):
        testassignment = baker.make('core.Assignment')
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
            .one('#devilry_admin_assignment_students_overview_button_create_groups')['href'])

    def test_buttonbar_create_groups_text(self):
        testassignment = baker.make('core.Assignment',
                                    parentnode__short_name='testperiod',
                                    parentnode__parentnode__short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Add students',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_overview_button_create_groups')
            .alltext_normalized)

    def test_buttonbar_merge_groups_link(self):
        testassignment = baker.make('core.Assignment')
        mock_cradmin_instance = self.__mockinstance_with_devilryrole('departmentadmin')

        def mock_reverse_url(appname, viewname, **kwargs):
            return '/{}/{}'.format(appname, viewname)

        mock_cradmin_instance.reverse_url = mock_reverse_url
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=mock_cradmin_instance)
        self.assertEqual(
            '/merge_groups/INDEX',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_overview_button_merge_groups')['href'])

    def test_buttonbar_merge_groups_text(self):
        testassignment = baker.make('core.Assignment',
                                    parentnode__short_name='testperiod',
                                    parentnode__parentnode__short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Organize students in project groups',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_overview_button_merge_groups')
            .alltext_normalized)

    def test_buttonbar_delete_groups_link(self):
        testassignment = baker.make('core.Assignment')
        mock_cradmin_instance = self.__mockinstance_with_devilryrole('departmentadmin')

        def mock_reverse_url(appname, viewname, **kwargs):
            return '/{}/{}'.format(appname, viewname)

        mock_cradmin_instance.reverse_url = mock_reverse_url
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=mock_cradmin_instance)
        self.assertEqual(
            '/delete_groups/INDEX',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_overview_button_delete_groups')['href'])

    def test_buttonbar_delete_groups_text(self):
        testassignment = baker.make('core.Assignment',
                                    parentnode__short_name='testperiod',
                                    parentnode__parentnode__short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Remove students',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_overview_button_delete_groups')
            .alltext_normalized)

    def test_groups_sanity(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testassignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        baker.make('core.AssignmentGroup', parentnode=testassignment, _quantity=3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            3,
            mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'))

    def test_anonymizationmode_fully_anonymous_subjectadmin_no_link(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
                requestuser=testuser)
        self.assertFalse(mockresponse.selector.exists(
            '.devilry-admin-assignment-students-overview-group-linkframe'))

    def test_anonymizationmode_fully_anonymous_departmentadmin_has_link(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
                requestuser=testuser)
        self.assertTrue(mockresponse.selector.exists(
            '.devilry-admin-assignment-students-overview-group-linkframe'))

    def test_anonymizationmode_semi_anonymous_subjectadmin_has_link(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
                requestuser=testuser)
        self.assertTrue(mockresponse.selector.exists(
            '.devilry-admin-assignment-students-overview-group-linkframe'))

    def test_anonymizationmode_off_subjectadmin_has_link(self):
        testuser = baker.make(settings.AUTH_USER_MODEL)
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode=baker.make_recipe(
                                   'devilry.apps.core.assignment_activeperiod_start',
                                   anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF))
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testgroup.assignment,
                cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
                requestuser=testuser)
        self.assertTrue(mockresponse.selector.exists(
            '.devilry-admin-assignment-students-overview-group-linkframe'))
