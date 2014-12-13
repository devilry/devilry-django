from mock import patch
from django.core.urlresolvers import reverse
from django.test import TestCase

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.soupselect import cssGet
from devilry.project.develop.testhelpers.soupselect import cssFind
from devilry.project.develop.testhelpers.soupselect import cssExists
from devilry.devilry_gradingsystem.pluginregistry import GradingSystemPluginRegistry

from .base import AdminViewTestMixin
from .base import MockApprovedPluginApi
from .base import MockPointsPluginApi
# from .base import MockRequiresConfigurationPluginApi



class TestSetPassingGradeMinPointsView(TestCase, AdminViewTestMixin):

    def setUp(self):
        self.admin1 = UserBuilder('admin1').user
        self.assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_admins(self.admin1)
        self.url = reverse('devilry_gradingsystem_admin_setpassing_grade_min_points', kwargs={
            'assignmentid': self.assignmentbuilder.assignment.id,
        })

    def test_invalid_pluginid_404(self):
        myregistry = GradingSystemPluginRegistry()
        self.assignmentbuilder.update(grading_system_plugin_id=1001)
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.get_as(self.admin1)
            self.assertEquals(response.status_code, 404)

    def test_render(self):
        myregistry = GradingSystemPluginRegistry()
        myregistry.add(MockPointsPluginApi)
        self.assignmentbuilder.update(grading_system_plugin_id=MockPointsPluginApi.id)
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.get_as(self.admin1)
            self.assertEquals(response.status_code, 200)
            html = response.content
            self.assertEquals(cssGet(html, '.page-header h1').text.strip(),
                'Set the minumum number of points required to pass')
            self.assertTrue(cssExists(html, '#id_passing_grade_min_points'))
            self.assertEquals(cssGet(html, '#id_passing_grade_min_points')['value'], '1')  # The default value

    def test_sets_passing_grade_min_points_automatically(self):
        myregistry = GradingSystemPluginRegistry()
        myregistry.add(MockApprovedPluginApi)
        self.assignmentbuilder.update(grading_system_plugin_id=MockApprovedPluginApi.id)
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.get_as(self.admin1)
            self.assertEquals(response.status_code, 302)
            self.assertTrue(response["Location"].endswith(
                reverse('devilry_gradingsystem_admin_summary', kwargs={
                    'assignmentid': self.assignmentbuilder.assignment.id})))
            self.assignmentbuilder.reload_from_db()
            self.assertEquals(self.assignmentbuilder.assignment.passing_grade_min_points,
                MockApprovedPluginApi(self.assignmentbuilder.assignment).get_passing_grade_min_points())

    def test_render_default_to_current_value(self):
        myregistry = GradingSystemPluginRegistry()
        myregistry.add(MockPointsPluginApi)
        self.assignmentbuilder.update(
            grading_system_plugin_id=MockPointsPluginApi.id,
            passing_grade_min_points=2030
        )
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.get_as(self.admin1)
            html = response.content
            self.assertEquals(cssGet(html, '#id_passing_grade_min_points')['value'], '2030')

    def test_render_custom_table(self):
        myregistry = GradingSystemPluginRegistry()
        myregistry.add(MockPointsPluginApi)
        self.assignmentbuilder.update(
            grading_system_plugin_id=MockPointsPluginApi.id,
            points_to_grade_mapper='custom-table')
        self.assignmentbuilder.assignment.get_point_to_grade_map().create_map(
            (0, 'Bad'),
            (30, 'Better'),
            (60, 'Good'))
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.get_as(self.admin1)
            self.assertEquals(response.status_code, 200)
            html = response.content
            self.assertEquals(cssGet(html, '.page-header h1').text.strip(),
                'Select the grade required to pass')
            self.assertTrue(cssExists(html, '#id_passing_grade_min_points'))
            self.assertEquals(len(cssFind(html, '#id_passing_grade_min_points option')), 3)
            self.assertEquals(cssGet(html, '#id_passing_grade_min_points option[value=0]').text.strip(), 'Bad')
            self.assertEquals(cssGet(html, '#id_passing_grade_min_points option[value=30]').text.strip(), 'Better')
            self.assertEquals(cssGet(html, '#id_passing_grade_min_points option[value=60]').text.strip(), 'Good')


    def test_post_valid_form(self):
        myregistry = GradingSystemPluginRegistry()
        myregistry.add(MockPointsPluginApi)
        self.assignmentbuilder.update(
            grading_system_plugin_id=MockPointsPluginApi.id,
            max_points=200 )
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.post_as(self.admin1, {
                'passing_grade_min_points': 100
            })
            self.assertEquals(response.status_code, 302)
            self.assertTrue(response["Location"].endswith(
                reverse('devilry_gradingsystem_admin_summary', kwargs={
                    'assignmentid': self.assignmentbuilder.assignment.id})))
            self.assignmentbuilder.reload_from_db()
            self.assertEquals(self.assignmentbuilder.assignment.passing_grade_min_points, 100)

    def test_post_negative_value_shows_error(self):
        myregistry = GradingSystemPluginRegistry()
        myregistry.add(MockPointsPluginApi)
        self.assignmentbuilder.update(
            grading_system_plugin_id=MockPointsPluginApi.id,
            passing_grade_min_points=10
        )
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.post_as(self.admin1, {
                'passing_grade_min_points': -1
            })
            self.assertEquals(response.status_code, 200)
            self.assertEquals(self.assignmentbuilder.assignment.passing_grade_min_points, 10) # Unchanged
            html = response.content
            self.assertIn('Ensure this value is greater than or equal to 0', html)

    def test_post_larger_than_max_points_shows_error(self):
        myregistry = GradingSystemPluginRegistry()
        myregistry.add(MockPointsPluginApi)
        self.assignmentbuilder.update(
            grading_system_plugin_id=MockPointsPluginApi.id,
            max_points=100,
            passing_grade_min_points=10
        )
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', myregistry):
            response = self.post_as(self.admin1, {
                'passing_grade_min_points': 200
            })
            self.assertEquals(response.status_code, 200)
            self.assertEquals(self.assignmentbuilder.assignment.passing_grade_min_points, 10) # Unchanged
            html = response.content
            self.assertIn('The minumum number of points required to pass must be less than the maximum number of points possible on the assignment', html)
