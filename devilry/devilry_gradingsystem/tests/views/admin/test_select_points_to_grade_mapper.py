import unittest
from mock import patch
from django.urls import reverse
from django.test import TestCase

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.soupselect import cssGet
from devilry.project.develop.testhelpers.soupselect import cssFind
from devilry.devilry_gradingsystem.pluginregistry import GradingSystemPluginRegistry

from .base import AdminViewTestMixin
from .base import MockApprovedPluginApi
from .base import MockPointsPluginApi


@unittest.skip('devilry_gradingsystem will most likely be replaced in 3.0')
class TestSelectPointsToGradeMapperView(TestCase, AdminViewTestMixin):

    def setUp(self):
        self.admin1 = UserBuilder('admin1').user
        self.assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_admins(self.admin1)
        self.url = reverse('devilry_gradingsystem_admin_select_points_to_grade_mapper', kwargs={
            'assignmentid': self.assignmentbuilder.assignment.id,
        })

    def test_invalid_pluginid_404(self):
        myregistry = GradingSystemPluginRegistry()
        self.assignmentbuilder.update(grading_system_plugin_id=1001)
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.get_as(self.admin1)
            self.assertEqual(response.status_code, 404)

    def test_render(self):
        myregistry = GradingSystemPluginRegistry()
        myregistry.add(MockPointsPluginApi)
        self.assignmentbuilder.update(grading_system_plugin_id=MockPointsPluginApi.id)
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.get_as(self.admin1)
            self.assertEqual(response.status_code, 200)
            html = response.content
            self.assertEqual(cssGet(html, '.page-header h1').text.strip(),
                'How are results presented to the student?')
            self.assertEqual(len(cssFind(html, '.devilry_gradingsystem_verbose_selectbox')), 3)

            self.assertEqual(cssGet(html, '.passed-failed_points_to_grade_mapper_box h2').text.strip(),
                'As passed or failed')
            self.assertEqual(cssGet(html, '.passed-failed_points_to_grade_mapper_box a.btn')['href'],
                '?points_to_grade_mapper=passed-failed')

            self.assertEqual(cssGet(html, '.raw-points_points_to_grade_mapper_box h2').text.strip(),
                'As points')
            self.assertEqual(cssGet(html, '.raw-points_points_to_grade_mapper_box a.btn')['href'],
                '?points_to_grade_mapper=raw-points')

            self.assertEqual(cssGet(html, '.custom-table_points_to_grade_mapper_box h2').text.strip(),
                'As a text looked up in a custom table')
            self.assertEqual(cssGet(html, '.custom-table_points_to_grade_mapper_box a.btn')['href'],
                '?points_to_grade_mapper=custom-table')

    def test_next_page_select_passing_grade_min_points(self):
        myregistry = GradingSystemPluginRegistry()
        myregistry.add(MockPointsPluginApi)
        self.assignmentbuilder.update(grading_system_plugin_id=MockPointsPluginApi.id)
        self.assertFalse(MockPointsPluginApi.sets_passing_grade_min_points_automatically)
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.get_as(self.admin1, {
                'points_to_grade_mapper': 'passed-failed'
            })
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response["Location"].endswith(
                reverse('devilry_gradingsystem_admin_setpassing_grade_min_points', kwargs={
                    'assignmentid': self.assignmentbuilder.assignment.id,
                })))
            self.assignmentbuilder.reload_from_db()
            self.assertEqual(self.assignmentbuilder.assignment.points_to_grade_mapper, 'passed-failed')

    def test_next_page_custom_table(self):
        myregistry = GradingSystemPluginRegistry()
        myregistry.add(MockPointsPluginApi)
        self.assignmentbuilder.update(grading_system_plugin_id=MockPointsPluginApi.id)
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.get_as(self.admin1, {
                'points_to_grade_mapper': 'custom-table'
            })
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response["Location"].endswith(
                reverse('devilry_gradingsystem_admin_setup_custom_table', kwargs={
                    'assignmentid': self.assignmentbuilder.assignment.id,
                })))
            self.assignmentbuilder.reload_from_db()
            self.assertEqual(self.assignmentbuilder.assignment.points_to_grade_mapper, 'custom-table')

    def test_next_page_finished(self):
        myregistry = GradingSystemPluginRegistry()
        myregistry.add(MockApprovedPluginApi)
        self.assignmentbuilder.update(grading_system_plugin_id=MockApprovedPluginApi.id)
        self.assertTrue(MockApprovedPluginApi.sets_passing_grade_min_points_automatically)
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.get_as(self.admin1, {
                'points_to_grade_mapper': 'passed-failed'
            })
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response["Location"].endswith(
                reverse('devilry_gradingsystem_admin_setpassing_grade_min_points', kwargs={
                    'assignmentid': self.assignmentbuilder.assignment.id,
                })))
            self.assignmentbuilder.reload_from_db()
            self.assertEqual(self.assignmentbuilder.assignment.points_to_grade_mapper, 'passed-failed')
