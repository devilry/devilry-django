from mock import patch
from django.core.urlresolvers import reverse
from django.test import TestCase

from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import cssFind
# from devilry_gradingsystem.pluginregistry import gradingsystempluginregistry
from devilry_gradingsystem.pluginregistry import GradingSystemPluginRegistry
from devilry_gradingsystem.pluginregistry import GradingSystemPluginInterface



class MockPointsPluginApi(GradingSystemPluginInterface):
    id = 'mock_gradingsystemplugin_points'
    title = 'Mock points'
    description = 'Mock points description.'

    def get_edit_feedback_url(self, deliveryid):
        return '/mock/points/edit_feedback/{}'.format(deliveryid)


class MockApprovedPluginApi(GradingSystemPluginInterface):
    id = 'mock_gradingsystemplugin_approved'
    title = 'Mock approved'
    description = 'Mock approved description.'
    sets_passing_grade_min_points_automatically = True
    sets_max_points_automatically = True

    def get_edit_feedback_url(self, deliveryid):
        return '/mock/approved/edit_feedback/{}'.format(deliveryid)

    def get_passing_grade_min_points(self):
        return 1

    def get_max_points(self):
        return 1


class MockRequiresConfigurationPluginApi(GradingSystemPluginInterface):
    id = 'mock_gradingsystemplugin_requiresconfiguration'
    title = 'Mock requiresconfiguration'
    description = 'Mock requiresconfiguration description.'
    requires_configuration = True

    def get_edit_feedback_url(self, deliveryid):
        return '/mock/requiresconfiguration/edit_feedback/{}'.format(deliveryid)

    def get_configuration_url(self):
        return '/mock/requiresconfiguration/configure/{}'.format(self.assignment.id)



class TestSelectPluginView(TestCase):
    def setUp(self):
        self.admin1 = UserBuilder('admin1').user
        self.assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_admins(self.admin1)

    def _login(self, user):
        self.client.login(username=user.username, password='test')

    def _get_as(self, user, *args, **kwargs):
        self._login(user)
        return self.client.get(reverse('devilry_gradingsystem_admin_selectplugin', kwargs={
            'assignmentid': self.assignmentbuilder.assignment.id,
        }), *args, **kwargs)

    def test_get_not_admin_404(self):
        nobody = UserBuilder('nobody').user
        response = self._get_as(nobody)
        self.assertEquals(response.status_code, 404)

    def test_get_not_admin_404_with_pluginselected(self):
        nobody = UserBuilder('nobody').user
        myregistry = GradingSystemPluginRegistry()
        myregistry.add(MockPointsPluginApi)
        with patch('devilry_gradingsystem.views.admin.selectplugin.gradingsystempluginregistry', myregistry):
            self.assertIn(MockPointsPluginApi.id, myregistry)
            response = self._get_as(nobody, {
                'selected_plugin_id': MockPointsPluginApi.id
            })
            self.assertEquals(response.status_code, 404)

    def test_render(self):
        myregistry = GradingSystemPluginRegistry()
        myregistry.add(MockPointsPluginApi)
        myregistry.add(MockApprovedPluginApi)
        with patch('devilry_gradingsystem.views.admin.selectplugin.gradingsystempluginregistry', myregistry):
            response = self._get_as(self.admin1)
            self.assertEquals(response.status_code, 200)
            html = response.content
            self.assertEquals(len(cssFind(html, '.devilry_gradingsystem_selectplugin_box')), 2)

    def test_next_page_requires_configuration(self):
        myregistry = GradingSystemPluginRegistry()
        myregistry.add(MockRequiresConfigurationPluginApi)
        with patch('devilry_gradingsystem.views.admin.selectplugin.gradingsystempluginregistry', myregistry):
            response = self._get_as(self.admin1, {
                'selected_plugin_id': MockRequiresConfigurationPluginApi.id
            })
            self.assertEquals(response.status_code, 302)
            self.assertEquals(response["Location"],
                'http://testserver/mock/requiresconfiguration/configure/{}'.format(
                    self.assignmentbuilder.assignment.id))