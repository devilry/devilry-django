# from mock import patch
from django.core.urlresolvers import reverse
from django.test import TestCase

from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import cssFind
# from devilry_gradingsystem.pluginregistry import GradingSystemPluginRegistry

from .base import AdminViewTestMixin
# from .base import MockApprovedPluginApi
# from .base import MockPointsPluginApi
# from .base import MockRequiresConfigurationPluginApi



class TestSetupCustomTableView(TestCase, AdminViewTestMixin):

    def setUp(self):
        self.admin1 = UserBuilder('admin1').user
        self.assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_admins(self.admin1)
        self.url = reverse('devilry_gradingsystem_admin_selectplugin', kwargs={
            'assignmentid': self.assignmentbuilder.assignment.id,
        })

    # def test_render(self):
    #     myregistry = GradingSystemPluginRegistry()
    #     myregistry.add(MockPointsPluginApi)
    #     myregistry.add(MockApprovedPluginApi)
    #     with patch('devilry_gradingsystem.views.admin.selectplugin.gradingsystempluginregistry', myregistry):
    #         response = self.get_as(self.admin1)
    #         self.assertEquals(response.status_code, 200)
    #         html = response.content
    #         self.assertEquals(cssGet(html, '.page-header h1').text.strip(),
    #             'How would you like to configure the plugin?')
    #         self.assertEquals(len(cssFind(html, '.devilry_gradingsystem_selectplugin_box')), 2)