from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.models import Deadline
from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.datebuilder import DateTimeBuilder
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import cssExists


class TestSearchView(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        # self.assignment1builder = PeriodBuilder.quickadd_ducku_duck1010_active()\
            # .add_assignment('assignment1', long_name='Assignment One')
        self.url = reverse('devilry_search')

    def _getas(self, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        return self.client.get(self.url, *args, **kwargs)

    def test_nologin(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_render_noinput(self):
        response = self._getas(self.testuser)
        self.assertEquals(response.status_code, 200)
        html = response.content
        self.assertEquals(cssGet(html, '#id_search').value, None)