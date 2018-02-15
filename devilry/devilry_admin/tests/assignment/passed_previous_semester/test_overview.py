from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core.models import Assignment
from devilry.devilry_admin.views.assignment.passed_previous_period import overview


class TestOverview(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.Overview

    def test_title(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment
        )
        self.assertEqual(
            mockresponse.selector.one('title').alltext_normalized,
            'Passed previous semester')

    def test_heading(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment
        )
        self.assertEqual(
            mockresponse.selector.one('.django-cradmin-page-header-inner > h1').alltext_normalized,
            'Passed previous semester')

    def test_assignment_grading_plugin_not_passed_failed(self):
        testassignment = mommy.make(
            'core.Assignment',
            grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment
        )
        self.assertEqual(
            mockresponse.selector.one(
                '.devilry-passed-previous-semester-unsupported-plugin-message > h3').alltext_normalized,
            'Unsupported grading plugin')

    def test_assignment_modes_list(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment
        )
        self.assertEqual(len(mockresponse.selector.list('.devilry-passed-previous-semester-mode-item-value')), 2)
        mode_title_list = [element.alltext_normalized for element in mockresponse.selector.list('.django-cradmin-listbuilder-itemvalue-titledescription-title')]
        self.assertIn('Manually pass students', mode_title_list)
        self.assertIn('Automatically pass students from an earlier semester', mode_title_list)
