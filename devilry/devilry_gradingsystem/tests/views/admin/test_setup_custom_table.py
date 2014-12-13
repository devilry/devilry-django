from mock import patch
from django.core.urlresolvers import reverse
from django.test import TestCase

from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.project.develop.testhelpers.soupselect import cssGet
from devilry.project.develop.testhelpers.soupselect import cssFind
from devilry.devilry_gradingsystem.pluginregistry import GradingSystemPluginRegistry

from .base import AdminViewTestMixin
from .base import MockPointsPluginApi



class TestSetupCustomTableView(TestCase, AdminViewTestMixin):

    def setUp(self):
        self.admin1 = UserBuilder('admin1').user
        self.myregistry = GradingSystemPluginRegistry()
        self.myregistry.add(MockPointsPluginApi)
        self.assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1',
                grading_system_plugin_id=MockPointsPluginApi.id,
                max_points=100,
                points_to_grade_mapper='custom-table'
            )\
            .add_admins(self.admin1)
        self.url = reverse('devilry_gradingsystem_admin_setup_custom_table', kwargs={
            'assignmentid': self.assignmentbuilder.assignment.id,
        })

    # def test_render(self):
    #     myregistry = GradingSystemPluginRegistry()
    #     myregistry.add(MockPointsPluginApi)
    #     myregistry.add(MockApprovedPluginApi)
    #     with patch('devilry.devilry_gradingsystem.views.admin.selectplugin.gradingsystempluginregistry', myregistry):
    #         response = self.get_as(self.admin1)
    #         self.assertEquals(response.status_code, 200)
    #         html = response.content
    #         self.assertEquals(cssGet(html, '.page-header h1').text.strip(),
    #             'How would you like to configure the plugin?')
    #         self.assertEquals(len(cssFind(html, '.devilry_gradingsystem_selectplugin_box')), 2)


    def test_post(self):
        with patch('devilry.apps.core.models.assignment.gradingsystempluginregistry', self.myregistry):
            response = self.post_as(self.admin1, {
                'form-0-grade': ['F'],
                'form-0-minimum_points': ['0'],
                'form-1-grade': ['C'],
                'form-1-minimum_points': ['50'],
                'form-INITIAL_FORMS': 0,
                'form-TOTAL_FORMS': 2
            })
            self.assertEquals(response.status_code, 302)
            self.assignmentbuilder.reload_from_db()
            self.assertFalse(self.assignmentbuilder.assignment.pointtogrademap.invalid)
            self.assertTrue(self.assignmentbuilder.assignment.has_valid_grading_setup())
