from django.test import TestCase
from django.core.urlresolvers import reverse

from devilry.project.develop.testhelpers.corebuilder import UserBuilder
# from develop.testhelpers.soupselect import cssFind
# from develop.testhelpers.soupselect import cssGet
# from develop.testhelpers.soupselect import cssExists
from devilry.project.develop.testhelpers.soupselect import cssExists, cssGet


class TestAboutMeView(TestCase):
    def setUp(self):
        self.testuserbuilder = UserBuilder('testuserbuilder')
        self.url = reverse('devilry_header_aboutme')

    def _getas(self, user, *args, **kwargs):
        self.client.login(username=user.username, password='test')
        return self.client.get(self.url, *args, **kwargs)

    def test_nologin(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_render_noinput(self):
        response = self._getas(self.testuserbuilder.user)
        self.assertEquals(response.status_code, 200)
        # html = response.content

    def test_languageselect(self):
        self.testuserbuilder.update_profile(
            languagecode='en'
        )
        with self.settings(LANGUAGES=[('en', 'English'), ('nb', 'Norwegian')]):
            html = self._getas(self.testuserbuilder.user).content
            self.assertTrue(cssExists(html,
                '#devilry_frontpage_languageselect #devilry_change_language_form'))
            self.assertEquals(
                cssGet(html, '#devilry_change_language_form option[value="en"]')['selected'],
                'selected')

    def test_languageselect_no_current_language(self):
        with self.settings(
                LANGUAGES=[('en', 'English'), ('nb', 'Norwegian')],
                LANGUAGE_CODE='nb'):
            html = self._getas(self.testuserbuilder.user).content
            self.assertTrue(cssExists(html,
                '#devilry_frontpage_languageselect #devilry_change_language_form'))
            self.assertEquals(
                cssGet(html, '#devilry_change_language_form option[value="nb"]')['selected'],
                'selected')
