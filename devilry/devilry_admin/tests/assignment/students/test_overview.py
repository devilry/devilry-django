import mock
from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_admin.views.assignment.students import overview


class TestOverview(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.Overview

    def test_title(self):
        testassignment = mommy.make('core.Assignment', long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertIn(
            'Students on Test Assignment',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment', long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Students on Test Assignment',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_choices_sanity(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            3,
            mockresponse.selector.count(
                    '#devilry_admin_assignment_students_overview_choices li'))

    def test_choice_create_groups_link(self):
        testassignment = mommy.make('core.Assignment')
        mock_cradmin_instance = mock.MagicMock()

        def mock_reverse_url(appname, viewname, **kwargs):
            return '/{}/{}'.format(appname, viewname)

        mock_cradmin_instance.reverse_url = mock_reverse_url
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
                                                          cradmin_instance=mock_cradmin_instance)
        self.assertEqual(
            '/create_groups/INDEX',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_overview_choice_create_groups a')['href'])

    def test_choice_create_groups_text(self):
        testassignment = mommy.make('core.Assignment',
                                    parentnode__short_name='testperiod',
                                    parentnode__parentnode__short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Add students',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_overview_choice_create_groups a')
            .alltext_normalized)

    def test_choice_merge_groups_link(self):
        testassignment = mommy.make('core.Assignment')
        mock_cradmin_instance = mock.MagicMock()

        def mock_reverse_url(appname, viewname, **kwargs):
            return '/{}/{}'.format(appname, viewname)

        mock_cradmin_instance.reverse_url = mock_reverse_url
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
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
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Organize students in project groups',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_overview_choice_merge_groups a')
            .alltext_normalized)

    def test_choice_delete_groups_link(self):
        testassignment = mommy.make('core.Assignment')
        mock_cradmin_instance = mock.MagicMock()

        def mock_reverse_url(appname, viewname, **kwargs):
            return '/{}/{}'.format(appname, viewname)

        mock_cradmin_instance.reverse_url = mock_reverse_url
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment,
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
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Delete students or project groups',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_overview_choice_delete_groups a')
            .alltext_normalized)

    def test_grouplist_no_groups(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'No students',
            mockresponse.selector.one('.django-cradmin-listbuilderview-no-items-message').alltext_normalized)
        self.assertFalse(
            mockresponse.selector.exists('.django-cradmin-listbuilder-list'))

    def test_grouplist_has_groups_sanity(self):
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertFalse(
            mockresponse.selector.exists('.django-cradmin-listbuilderview-no-items-message'))
        self.assertTrue(
            mockresponse.selector.exists('.django-cradmin-listbuilder-list'))

    # def test_grouplist_render_single

    # def test_grouplist_ordering

    # def test_grouplist_pagination(self):
