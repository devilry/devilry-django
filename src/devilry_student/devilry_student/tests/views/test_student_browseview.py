from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.apps.core.models import GroupInvite
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import prettyhtml
from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.corebuilder import NodeBuilder
from devilry_developer.testhelpers.corebuilder import SubjectBuilder


class TestBrowseView(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.url = reverse('devilry_student_browse')

    def _getas(self, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        return self.client.get(self.url, *args, **kwargs)

    def _postas(self, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        return self.client.post(self.url, *args, **kwargs)

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, expected_url='http://testserver/authenticate/login?next=/devilry_student/browse/', 
            status_code=302, target_status_code=200)

    def test_render_header(self):
        response = self._getas(self.testuser)
        html = response.content
        self.assertEquals(cssGet(html, '.page-header h1').text.strip(), "Browse")
        self.assertEquals(cssGet(html, '.page-header .subheader').text.strip(), "Browse all your courses")

    def test_period_list(self):
        node = SubjectBuilder.quickadd_ducku_duck1010()
        period1 = node.add_6month_active_period()
        period2 = node.add_6month_lastyear_period()

        student1 = UserBuilder('student1').user

        period1.add_relatedstudents(self.testuser, student1)
        period2.add_relatedstudents(self.testuser)

        response = self._getas(self.testuser)
        html = response.content
        self.assertEquals(len(cssFind(html, '.period-list-element')), 2)

        response = self._getas(student1)
        html = response.content
        self.assertEquals(len(cssFind(html, '.period-list-element')), 1)