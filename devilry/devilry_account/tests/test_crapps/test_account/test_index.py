from django import test
from django.conf import settings
from django.test import override_settings
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_account.crapps import account


class TestIndexView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = account.index.IndexView

    def test_get_title(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL,
                                 shortname='test',
                                 fullname='Test')
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         'Test (test) - Account')

    def test_get_h1(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(mockresponse.selector.one('.test-primary-h1').alltext_normalized,
                         'Account overview')

    def test_get_fullname_none(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(mockresponse.selector.one('.test-fullname').alltext_normalized,
                         'Name not registered for account')

    def test_get_fullname(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL,
                                 fullname='Test User')
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(mockresponse.selector.one('.test-fullname').alltext_normalized,
                         'Test User')

    def test_get_shortname(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL,
                                 shortname='testuser')
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(mockresponse.selector.one('.test-shortname').alltext_normalized,
                         'testuser')

    def _get_emails_from_selector(self, selector):
        return [element.alltext_normalized for element in selector.list('.test-email')]

    def test_get_email_addresses_single(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.UserEmail', email='test@example.com',
                   user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(self._get_emails_from_selector(mockresponse.selector),
                         ['test@example.com'])
        self.assertEqual(mockresponse.selector.one('.test-emails-title').alltext_normalized,
                         'Email address')

    def test_get_email_addresses_multiple(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.UserEmail', email='test1@example.com',
                   user=requestuser)
        mommy.make('devilry_account.UserEmail', email='test2@example.com',
                   user=requestuser, use_for_notifications=False)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(set(self._get_emails_from_selector(mockresponse.selector)),
                         {'test1@example.com (use for notifications)', 'test2@example.com'})
        self.assertEqual(mockresponse.selector.one('.test-emails-title').alltext_normalized,
                         'Email addresses')

    def _get_usernames_from_selector(self, selector):
        return [element.alltext_normalized for element in selector.list('.test-username')]

    @override_settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True)
    def test_get_usernames_email_auth_backend_true(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.UserName', username='test',
                   user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertFalse(mockresponse.selector.exists('.test-usernames-title'))
        self.assertFalse(mockresponse.selector.exists('.test-username'))

    @override_settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False)
    def test_get_usernames_single(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.UserName', username='test',
                   user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(self._get_usernames_from_selector(mockresponse.selector),
                         ['test'])
        self.assertEqual(mockresponse.selector.one('.test-usernames-title').alltext_normalized,
                         'Username')

    @override_settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False)
    def test_get_usernames_multiple(self):
        requestuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('devilry_account.UserName', username='test1',
                   user=requestuser)
        mommy.make('devilry_account.UserName', username='test2',
                   user=requestuser)
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=requestuser)
        self.assertEqual(set(self._get_usernames_from_selector(mockresponse.selector)),
                         {'test1', 'test2'})
        self.assertEqual(mockresponse.selector.one('.test-usernames-title').alltext_normalized,
                         'Usernames')
