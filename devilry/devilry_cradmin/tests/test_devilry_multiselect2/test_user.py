import htmls
import mock
from django import test
from django import forms
from django.conf import settings
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.devilry_cradmin import devilry_multiselect2


class TestSelectedItem(test.TestCase):
    def test_title_without_fullname(self):
        user = baker.make(settings.AUTH_USER_MODEL,
                          shortname='test@example.com',
                          fullname='')
        selector = htmls.S(devilry_multiselect2.user.SelectedItem(value=user).render())
        self.assertEqual(
                'test@example.com',
                selector.one('.cradmin-legacy-multiselect2-target-selected-item-title').alltext_normalized)

    def test_title_with_fullname(self):
        user = baker.make(settings.AUTH_USER_MODEL,
                          fullname='Test User',
                          shortname='test@example.com')
        selector = htmls.S(devilry_multiselect2.user.SelectedItem(value=user).render())
        self.assertEqual(
                'Test User',
                selector.one('.cradmin-legacy-multiselect2-target-selected-item-title').alltext_normalized)

    def test_description_without_fullname(self):
        user = baker.make(settings.AUTH_USER_MODEL,
                          shortname='test@example.com',
                          fullname='')
        selector = htmls.S(devilry_multiselect2.user.SelectedItem(value=user).render())
        self.assertFalse(
                selector.exists('.cradmin-legacy-multiselect2-target-selected-item-description'))

    def test_description_with_fullname(self):
        user = baker.make(settings.AUTH_USER_MODEL,
                          fullname='Test User',
                          shortname='test@example.com')
        selector = htmls.S(devilry_multiselect2.user.SelectedItem(value=user).render())
        self.assertEqual(
                'test@example.com',
                selector.one('.cradmin-legacy-multiselect2-target-selected-item-description').alltext_normalized)


class TestItemValue(test.TestCase):
    def test_title_without_fullname(self):
        user = baker.make(settings.AUTH_USER_MODEL,
                          shortname='test@example.com',
                          fullname='')
        selector = htmls.S(devilry_multiselect2.user.ItemValue(value=user).render())
        self.assertEqual(
                'test@example.com',
                selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_title_with_fullname(self):
        user = baker.make(settings.AUTH_USER_MODEL,
                          fullname='Test User',
                          shortname='test@example.com')
        selector = htmls.S(devilry_multiselect2.user.ItemValue(value=user).render())
        self.assertEqual(
                'Test User',
                selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description_without_fullname(self):
        user = baker.make(settings.AUTH_USER_MODEL,
                          shortname='test@example.com',
                          fullname='')
        selector = htmls.S(devilry_multiselect2.user.ItemValue(value=user).render())
        self.assertFalse(
                selector.exists('.cradmin-legacy-listbuilder-itemvalue-titledescription-description'))

    def test_description_with_fullname(self):
        user = baker.make(settings.AUTH_USER_MODEL,
                          fullname='Test User',
                          shortname='test@example.com')
        selector = htmls.S(devilry_multiselect2.user.ItemValue(value=user).render())
        self.assertEqual(
                'test@example.com',
                selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized)


class TestTarget(test.TestCase):
    def test_with_items_title(self):
        selector = htmls.S(devilry_multiselect2.user.Target(form=forms.Form()).render(request=mock.MagicMock()))
        self.assertEqual(
                'Selected users',
                selector.one('.cradmin-legacy-multiselect2-target-title').alltext_normalized)

    def test_without_items_text(self):
        selector = htmls.S(devilry_multiselect2.user.Target(form=forms.Form()).render(request=mock.MagicMock()))
        self.assertEqual(
                'No users selected',
                selector.one('.cradmin-legacy-multiselect2-target-without-items-content').alltext_normalized)


class MockMultiselectUsersView(devilry_multiselect2.user.BaseMultiselectUsersView):
    def get_filterlist_url(self, filters_string):
        return '/{}'.format(filters_string)


class TestBaseMultiselectUsersView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = MockMultiselectUsersView

    def test_render_sanity(self):
        # Only a sanity test - we do not repeat all the tests from TestItemValue
        baker.make(settings.AUTH_USER_MODEL,
                   fullname='Test User',
                   shortname='test@example.com')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=mock.MagicMock())
        self.assertEqual(
            'Test User',
            mockresponse.selector.one(
                    '.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)
        self.assertEqual(
            'test@example.com',
            mockresponse.selector.one(
                    '.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized)

    def __get_titles(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]

    def test_ordering(self):
        baker.make(settings.AUTH_USER_MODEL,
                   shortname='userb')
        baker.make(settings.AUTH_USER_MODEL,
                   shortname='usera')
        baker.make(settings.AUTH_USER_MODEL,
                   shortname='userc')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=mock.MagicMock())
        self.assertEqual(
                ['usera', 'userb', 'userc'],
                self.__get_titles(mockresponse.selector))

    def test_selectall_not_available(self):
        baker.make(settings.AUTH_USER_MODEL)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=mock.MagicMock())
        self.assertFalse(mockresponse.selector.exists('.cradmin-legacy-multiselect2-listcolumn-buttons .btn'))

    def test_search_shortname(self):
        baker.make(settings.AUTH_USER_MODEL,
                   shortname='userb')
        baker.make(settings.AUTH_USER_MODEL,
                   shortname='usera')
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=mock.MagicMock(),
                viewkwargs={'filters_string': 'search-usera'})
        self.assertEqual(
                {'usera'},
                set(self.__get_titles(mockresponse.selector)))

    def test_search_fullname(self):
        baker.make(settings.AUTH_USER_MODEL,
                   fullname='Userb')
        baker.make(settings.AUTH_USER_MODEL,
                   fullname='Usera')
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=mock.MagicMock(),
                viewkwargs={'filters_string': 'search-usera'})
        self.assertEqual(
                {'Usera'},
                set(self.__get_titles(mockresponse.selector)))

    def test_search_username(self):
        baker.make('devilry_account.UserName',
                   user__fullname='Test User 1',
                   username='testuser1')
        baker.make('devilry_account.UserName',
                   user__fullname='Test User 2',
                   username='testuser2')
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=mock.MagicMock(),
                viewkwargs={'filters_string': 'search-testuser1'})
        self.assertEqual(
                {'Test User 1'},
                set(self.__get_titles(mockresponse.selector)))

    def test_search_useremail(self):
        baker.make('devilry_account.UserEmail',
                   user__fullname='Test User 1',
                   email='testuser1@example.com')
        baker.make('devilry_account.UserEmail',
                   user__fullname='Test User 2',
                   email='testuser2@example.com')
        mockresponse = self.mock_http200_getrequest_htmls(
                requestuser=mock.MagicMock(),
                viewkwargs={'filters_string': 'search-testuser1'})
        self.assertEqual(
                {'Test User 1'},
                set(self.__get_titles(mockresponse.selector)))
