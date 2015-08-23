from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from devilry.devilry_rest.testclient import RestClient
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

    def _get_languagecode(self, username):
        user = get_user_model().objects.get(username=username)
        return user.languagecode

    def _set_languagecode(self, username, languagecode):
        user = get_user_model().objects.get(username=username)
        user.languagecode = languagecode
        user.save()

    def test_get_languagecode_none(self):
        self.assertEquals(self._get_languagecode('testuser'), None)
        content, response = self._getas('testuser')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['preferred'], None)
        self.assertEquals(content['selected']['languagecode'],
                          settings.LANGUAGE_CODE)

    def test_get_languagecode_set(self):
        self._set_languagecode('testuser', 'nb')
        content, response = self._getas('testuser')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['preferred'], 'nb')
        self.assertEquals(content['selected']['languagecode'], 'nb')

    def _putas(self, username, data):
        self.client.login(username=username, password='test')
        return self.client.rest_put(self.url, data)

    def test_put(self):
        content, response = self._putas('testuser', {'preferred': 'nb'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['preferred'], 'nb')
        self.assertEquals(self._get_languagecode('testuser'), 'nb')

    def test_put_invalid(self):
        content, response = self._putas('testuser', {'preferred': 'invalid-code'})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(content['field_errors']['preferred'],
                          [u'Invalid languagecode: invalid-code'])

    def test_put_with_extradata(self):
        content, response = self._putas('testuser', {'preferred': 'nb',
                                                     'selected': {'ignored': 'data'},
                                                     'available': ['ignored']})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['preferred'], 'nb')
        self.assertEquals(self._get_languagecode('testuser'), 'nb')
