from django import test
from django_cradmin import cradmin_testhelpers
from mock import mock
from model_mommy import mommy

from devilry.devilry_account.crapps.account import select_language
from devilry.devilry_account.models import User


class TestSelectLanguagePostView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = select_language.SelectLanguageView

    def __make_mock_request(self, **kwargs):
        mockrequest = mock.MagicMock()
        mockrequest.session = self.client.session
        return mockrequest

    def test_get_rendered_languages(self):
        mockresponse = self.mock_http200_getrequest_htmls()
        buttons_text = [element.alltext_normalized for element in mockresponse.selector.list('.button')]
        self.assertIn('English en', buttons_text)
        self.assertIn('Norwegian Bokmal nb', buttons_text)

    def test_no_selected_language(self):
        mockrequest = self.__make_mock_request()
        mockresponse = self.mock_http302_postrequest(
            sessionmock=mockrequest.session,
            requestkwargs={
                'data': {
                    'selected_language': ''
                }
            },
        )
        self.assertEqual(mockresponse.request.session['SELECTED_LANGUAGE_CODE'], 'en')

    def test_selected_language_not_in_settings(self):
        mockrequest = self.__make_mock_request()
        mockresponse = self.mock_http302_postrequest(
            sessionmock=mockrequest.session,
            requestkwargs={
                'data': {
                    'selected_language': 'de'
                }
            },
        )
        self.assertEqual(mockresponse.request.session['SELECTED_LANGUAGE_CODE'], 'en')

    def test_selected_language_sanity(self):
        mockrequest = self.__make_mock_request()
        mockresponse = self.mock_http302_postrequest(
            sessionmock=mockrequest.session,
            requestkwargs={
                'data': {
                    'selected_language': 'nb'
                }
            },
        )
        self.assertEqual(mockresponse.request.session['SELECTED_LANGUAGE_CODE'], 'nb')

    def test_change_languagecode_on_user(self):
        user = mommy.make('devilry_account.User', languagecode='en')
        mockrequest = self.__make_mock_request()
        self.mock_http302_postrequest(
            requestuser=user,
            sessionmock=mockrequest.session,
            requestkwargs={
                'data': {
                    'selected_language': 'nb'
                }
            },
        )
        user = User.objects.get(id=user.id)
        self.assertEqual(user.languagecode, 'nb')

    def test_selected_language_user_authenticated(self):
        user = mommy.make('devilry_account.User', languagecode='en')
        mockrequest = self.__make_mock_request()
        mockresponse = self.mock_http302_postrequest(
            requestuser=user,
            sessionmock=mockrequest.session,
            requestkwargs={
                'data': {
                    'selected_language': 'nb'
                }
            },
        )
        self.assertEqual(mockresponse.request.session['SELECTED_LANGUAGE_CODE'], 'nb')
