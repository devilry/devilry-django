from django import test
from django.http import HttpResponse
from django.test import override_settings
from django.utils import translation
from mock import mock
from model_mommy import mommy

from devilry.devilry_account import middleware


@override_settings(
    LANGUAGE_CODE='en',
    LANGUAGES=[
        ('en', 'English'),
        ('nb', 'Norwegian Bokmal'),
    ]
)
class TestAccountMiddleware(test.TestCase):
    def tearDown(self):
        translation.deactivate_all()

    def __make_mock_request(self, user=None, is_authenticated=False, languagecode='en'):
        mockrequest = mock.MagicMock()
        mockrequest.session = self.client.session
        mockrequest.session['SELECTED_LANGUAGE_CODE'] = languagecode
        mockrequest.user = user or mock.MagicMock()
        mockrequest.user.is_authenticated.return_value = is_authenticated
        return mockrequest

    def test_process_request_unauthenticated_user(self):
        local_middleware = middleware.LocalMiddleware()
        mockrequest = self.__make_mock_request(languagecode='nb')
        local_middleware.process_request(request=mockrequest)
        self.assertEqual('nb', translation.get_language())
        self.assertEqual('nb', mockrequest.LANGUAGE_CODE)

    def test_process_request_authenticated_user(self):
        local_middleware = middleware.LocalMiddleware()
        user = mommy.make('devilry_account.User', languagecode='nb')
        mockrequest = self.__make_mock_request(user=user, is_authenticated=True)
        local_middleware.process_request(request=mockrequest)
        self.assertEqual('nb', translation.get_language())
        self.assertEqual('nb', mockrequest.LANGUAGE_CODE)

    def test_process_response(self):
        local_middleware = middleware.LocalMiddleware()
        translation.activate('nb')
        mockrequest = self.__make_mock_request(languagecode='nb')
        response = local_middleware.process_response(request=mockrequest, response=HttpResponse())
        self.assertEqual('nb', response['Content-Language'])
