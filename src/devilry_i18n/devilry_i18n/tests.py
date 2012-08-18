from django.test import TestCase
from django.contrib.auth.models import User

from devilry.utils.rest_testclient import RestClient
from devilry.apps.core.testhelper import TestHelper



class TestLanguageSelect(TestCase):
    def setUp(self):
        self.client = RestClient()

        self.url = '/devilry_i18n/rest/languageselect'
        self.testhelper = TestHelper()
        self.testhelper.create_user('testuser')

    def _getas(self, username):
        self.client.login(username=username, password='test')
        return self.client.rest_get(self.url)

    def test_get(self):
        content, response = self._getas('testuser')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['preferred']['languagecode'], 'en')

    def _putas(self, username, data):
        self.client.login(username=username, password='test')
        return self.client.rest_put(self.url, data)

    def test_put(self):
        content, response = self._putas('testuser', {'languagecode': 'no'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['preferred']['languagecode'], 'no')
        testuser = User.objects.get(username='testuser')
        self.assertEquals(testuser.devilryuserprofile.languagecode, 'no')
