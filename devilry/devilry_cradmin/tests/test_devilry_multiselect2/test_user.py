import htmls
import mock
from django import test
from django import forms
from django.conf import settings
from model_mommy import mommy

from devilry.devilry_cradmin import devilry_multiselect2


class TestSelectedItem(test.TestCase):
    def test_title_without_fullname(self):
        user = mommy.make(settings.AUTH_USER_MODEL,
                          shortname='test@example.com',
                          fullname='')
        selector = htmls.S(devilry_multiselect2.user.SelectedItem(value=user).render())
        self.assertEqual(
                'test@example.com',
                selector.one('.django-cradmin-multiselect2-target-selected-item-title').alltext_normalized)

    def test_title_with_fullname(self):
        user = mommy.make(settings.AUTH_USER_MODEL,
                          fullname='Test User',
                          shortname='test@example.com')
        selector = htmls.S(devilry_multiselect2.user.SelectedItem(value=user).render())
        self.assertEqual(
                'Test User',
                selector.one('.django-cradmin-multiselect2-target-selected-item-title').alltext_normalized)

    def test_description_without_fullname(self):
        user = mommy.make(settings.AUTH_USER_MODEL,
                          shortname='test@example.com',
                          fullname='')
        selector = htmls.S(devilry_multiselect2.user.SelectedItem(value=user).render())
        self.assertFalse(
                selector.exists('.django-cradmin-multiselect2-target-selected-item-description'))

    def test_description_with_fullname(self):
        user = mommy.make(settings.AUTH_USER_MODEL,
                          fullname='Test User',
                          shortname='test@example.com')
        selector = htmls.S(devilry_multiselect2.user.SelectedItem(value=user).render())
        self.assertEqual(
                'test@example.com',
                selector.one('.django-cradmin-multiselect2-target-selected-item-description').alltext_normalized)


class TestItemValue(test.TestCase):
    def test_title_without_fullname(self):
        user = mommy.make(settings.AUTH_USER_MODEL,
                          shortname='test@example.com',
                          fullname='')
        selector = htmls.S(devilry_multiselect2.user.ItemValue(value=user).render())
        self.assertEqual(
                'test@example.com',
                selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_title_with_fullname(self):
        user = mommy.make(settings.AUTH_USER_MODEL,
                          fullname='Test User',
                          shortname='test@example.com')
        selector = htmls.S(devilry_multiselect2.user.ItemValue(value=user).render())
        self.assertEqual(
                'Test User',
                selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description_without_fullname(self):
        user = mommy.make(settings.AUTH_USER_MODEL,
                          shortname='test@example.com',
                          fullname='')
        selector = htmls.S(devilry_multiselect2.user.ItemValue(value=user).render())
        self.assertFalse(
                selector.exists('.django-cradmin-listbuilder-itemvalue-titledescription-description'))

    def test_description_with_fullname(self):
        user = mommy.make(settings.AUTH_USER_MODEL,
                          fullname='Test User',
                          shortname='test@example.com')
        selector = htmls.S(devilry_multiselect2.user.ItemValue(value=user).render())
        self.assertEqual(
                'test@example.com',
                selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)


class TestTarget(test.TestCase):
    def test_with_items_title(self):
        selector = htmls.S(devilry_multiselect2.user.Target(form=forms.Form()).render(request=mock.MagicMock()))
        self.assertEqual(
                'Selected users',
                selector.one('.django-cradmin-multiselect2-target-title').alltext_normalized)

    def test_without_items_text(self):
        selector = htmls.S(devilry_multiselect2.user.Target(form=forms.Form()).render(request=mock.MagicMock()))
        self.assertEqual(
                'No users selected',
                selector.one('.django-cradmin-multiselect2-target-without-items-content').alltext_normalized)
