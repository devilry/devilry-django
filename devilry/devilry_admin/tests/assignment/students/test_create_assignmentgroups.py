from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_admin.views.assignment.students import create_assignmentgroups


class TestOverview(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = create_assignmentgroups.Overview

    def test_title(self):
        testassignment = mommy.make('core.Assignment',
                                    short_name='testassignment',
                                    parentnode__short_name='testperiod',
                                    parentnode__parentnode__short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertIn(
            'Add students to testsubject.testperiod.testassignment',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Add students',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_header_lead_text(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'How would you like to add students?',
            mockresponse.selector.one('.django-cradmin-page-header-inner .lead').alltext_normalized)

    def test_choices_sanity(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            2,
            mockresponse.selector.count(
                    '#devilry_admin_assignment_students_create_assignmentgroups_overview_choices li'))

    def test_choice_all_link(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            '#',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_create_assignmentgroups_overview_choice_all a')['href'])

    def test_choice_all_text(self):
        testassignment = mommy.make('core.Assignment',
                                    parentnode__short_name='testperiod',
                                    parentnode__parentnode__short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Add all students registered on testsubject.testperiod',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_create_assignmentgroups_overview_choice_all a')
            .alltext_normalized)

    def test_choice_select_link(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            '#',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_create_assignmentgroups_overview_choice_select a')['href'])

    def test_choice_select_text(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Select students manually',
            mockresponse.selector
            .one('#devilry_admin_assignment_students_create_assignmentgroups_overview_choice_select a')
            .alltext_normalized)
