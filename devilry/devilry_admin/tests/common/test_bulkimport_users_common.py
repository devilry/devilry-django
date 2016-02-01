from django.test import TestCase
from django_cradmin import cradmin_testhelpers

from devilry.devilry_admin.views.common.bulkimport_users_common import AbstractTypeInUsersView


class AbstractTypeInUsersViewTestMixin(cradmin_testhelpers.TestCaseMixin):
    def test_get_render_form(self):
        mockresponse = self.mock_http200_getrequest_htmls()
        self.assertTrue(mockresponse.selector.exists('textarea#id_users_blob'))

    def test_get_render_form_help_text_email_backend(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            mockresponse = self.mock_http200_getrequest_htmls()
            self.assertEqual(mockresponse.selector.one('#hint_id_users_blob').alltext_normalized,
                             'Type or paste in email addresses separated '
                             'by comma (","), space or one user on each line.')

    def test_get_render_form_help_text_username_backend(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            mockresponse = self.mock_http200_getrequest_htmls()
            self.assertEqual(mockresponse.selector.one('#hint_id_users_blob').alltext_normalized,
                             'Type or paste in usernames separated '
                             'by comma (","), space or one user on each line.')

    def test_get_render_form_placeholder_email_backend(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            mockresponse = self.mock_http200_getrequest_htmls()
            self.assertEqual(mockresponse.selector.one('#id_users_blob')['placeholder'],
                             'jane@example.com\njohn@example.com')

    def test_get_render_form_placeholder_username_backend(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            mockresponse = self.mock_http200_getrequest_htmls()
            self.assertEqual(mockresponse.selector.one('#id_users_blob')['placeholder'],
                             'jane\njohn')

    def test_post_blank(self):
        mockresponse = self.mock_http200_postrequest_htmls()
        self.assertEqual('This field is required.',
                         mockresponse.selector.one('#error_1_id_users_blob').alltext_normalized)

    def test_post_invalid_emails_simple(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            mockresponse = self.mock_http200_postrequest_htmls(requestkwargs=dict(data={
                'users_blob': 'test'
            }))
            self.assertEqual('Invalid email addresses: test',
                             mockresponse.selector.one('#error_1_id_users_blob').alltext_normalized)

    def test_post_invalid_emails_multiple(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True):
            mockresponse = self.mock_http200_postrequest_htmls(requestkwargs=dict(data={
                'users_blob': 'test,test2@example.com,test3@@example.com'
            }))
            self.assertEqual('Invalid email addresses: test, test3@@example.com',
                             mockresponse.selector.one('#error_1_id_users_blob').alltext_normalized)

    def test_post_invalid_usernames_simple(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            mockresponse = self.mock_http200_postrequest_htmls(requestkwargs=dict(data={
                'users_blob': 'Test'
            }))
            self.assertEqual('Invalid usernames: Test',
                             mockresponse.selector.one('#error_1_id_users_blob').alltext_normalized)

    def test_post_invalid_usernames_multiple(self):
        with self.settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=False):
            mockresponse = self.mock_http200_postrequest_htmls(requestkwargs=dict(data={
                'users_blob': 'test,test2@example.com,test3.ing,Test4,test5'
            }))
            self.assertEqual('Invalid usernames: Test4, test2@example.com, test3.ing',
                             mockresponse.selector.one('#error_1_id_users_blob').alltext_normalized)


class MockTypeInUsersView(AbstractTypeInUsersView):
    def get_backlink_label(self):
        return 'Back'

    def get_backlink_url(self):
        return '/back'


class TestAbstractTypeInUsersView(TestCase, AbstractTypeInUsersViewTestMixin):
    viewclass = MockTypeInUsersView

    def test_split_users_blob_empty(self):
        self.assertEqual(
            set(),
            AbstractTypeInUsersView.split_users_blob(''))

    def test_split_users_blob_single(self):
        self.assertEqual(
            {'test@example.com'},
            AbstractTypeInUsersView.split_users_blob('test@example.com'))

    def test_split_users_blob_multiple(self):
        self.assertEqual(
            {'test@example.com', 'test2@example.com', 'test3@example.com'},
            AbstractTypeInUsersView.split_users_blob('test@example.com test2@example.com test3@example.com'))

    def test_split_users_blob_newlines(self):
        self.assertEqual(
            {'test@example.com', 'test2@example.com', 'test3@example.com'},
            AbstractTypeInUsersView.split_users_blob('test@example.com\ntest2@example.com\ntest3@example.com'))

    def test_split_users_blob_comma(self):
        self.assertEqual(
            {'test@example.com', 'test2@example.com', 'test3@example.com'},
            AbstractTypeInUsersView.split_users_blob('test@example.com,test2@example.com,test3@example.com'))

    def test_split_users_blob_semicolon(self):
        self.assertEqual(
            {'test@example.com', 'test2@example.com', 'test3@example.com'},
            AbstractTypeInUsersView.split_users_blob('test@example.com;test2@example.com;test3@example.com'))

    def test_split_users_blob_messy_middle(self):
        self.assertEqual(
            {'test@example.com', 'test2@example.com', 'test3@example.com'},
            AbstractTypeInUsersView.split_users_blob('test@example.com, \ntest2@example.com'
                                                     '\n,\n,  test3@example.com'))

    def test_split_users_blob_messy_suffix(self):
        self.assertEqual(
            {'test@example.com'},
            AbstractTypeInUsersView.split_users_blob('test@example.com, \n;\n,'))

    def test_split_users_blob_messy_prefix(self):
        self.assertEqual(
            {'test@example.com'},
            AbstractTypeInUsersView.split_users_blob(', ;\n\n,\ntest@example.com'))

    def test_split_users_blob_messy_everywhere(self):
        self.assertEqual(
            {'test@example.com', 'test2@example.com', 'test3@example.com'},
            AbstractTypeInUsersView.split_users_blob('  \n,,; \n, test@example.com, ,;,\ntest2@example.com'
                                                     '\n,\n,  test3@example.com,,,,\n,  \n,  '))
