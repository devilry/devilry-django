from django.test import TestCase
from django.core.urlresolvers import reverse

# from devilry_developer.testhelpers.corebuilder import SubjectBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_developer.testhelpers.soupselect import cssFind
from devilry_developer.testhelpers.soupselect import cssGet
from devilry_developer.testhelpers.soupselect import cssExists
from devilry_developer.testhelpers.login import LoginTestCaseMixin



class TestFrontpage(TestCase, LoginTestCaseMixin):
    def setUp(self):
        self.url = reverse('devilry_frontpage')
        self.testuser = UserBuilder('testuser').user

    def test_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_authenticated(self):
        response = self.get_as(self.testuser, self.url)
        self.assertEquals(response.status_code, 200)
    
    def test_helplinks(self):
        html = self.get_as(self.testuser, self.url).content
        self.assertTrue(cssExists(html, '#devilry_frontpage_helplinks'))
        self.assertEquals(
            cssGet(html, '#devilry_frontpage_helplinks ul li a').text.strip(),
            'Official Devilry documentation')

    def test_changelanguage(self):
        html = self.get_as(self.testuser, self.url).content
        self.assertTrue(cssExists(html, '#devilry_frontpage_languageselect #devilry_change_language_form'))