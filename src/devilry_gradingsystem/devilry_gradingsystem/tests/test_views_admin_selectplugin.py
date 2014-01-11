from django.core.urlresolvers import reverse
from django.test import TestCase

from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_gradingsystem.pluginregistry import gradingsystempluginregistry


class TestSelectPluginView(TestCase):
    def setUp(self):
        self.admin1 = UserBuilder('admin1').user
        self.assignmentbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            .add_assignment('assignment1')\
            .add_admins(self.admin1)

    def _login(self, user):
        self.client.login(username=user.username, password='test')

    def _get_as(self, user):
        self._login(user)
        return self.client.get(reverse('devilry_gradingsystem_admin_selectplugin', kwargs={
            'assignmentid': self.assignmentbuilder.assignment.id,
        }))

    def test_get_not_admin_404(self):
        nobody = UserBuilder('nobody').user
        response = self._get_as(nobody)
        self.assertEquals(response.status_code, 404)

    def test_render(self):
        response = self._get_as(self.admin1)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(len(cssFind(html, '.devilry_gradingsystem_selectplugin_box')), len(gradingsystempluginregistry))
