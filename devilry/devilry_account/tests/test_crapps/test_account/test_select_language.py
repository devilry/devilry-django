from django import test
from django_cradmin import cradmin_testhelpers
from mock import mock

from devilry.devilry_account.crapps.account import select_language


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
