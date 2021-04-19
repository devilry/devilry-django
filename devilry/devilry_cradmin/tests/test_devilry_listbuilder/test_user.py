import htmls
from django import test
from django.conf import settings
from model_bakery import baker

from devilry.devilry_cradmin import devilry_listbuilder


class TestItemValue(test.TestCase):
    def test_title_without_fullname(self):
        user = baker.make(settings.AUTH_USER_MODEL,
                          shortname='test@example.com',
                          fullname='')
        selector = htmls.S(devilry_listbuilder.user.ItemValue(value=user).render())
        self.assertEqual(
                'test@example.com',
                selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_title_with_fullname(self):
        user = baker.make(settings.AUTH_USER_MODEL,
                          fullname='Test User',
                          shortname='test@example.com')
        selector = htmls.S(devilry_listbuilder.user.ItemValue(value=user).render())
        self.assertEqual(
                'Test User',
                selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description_without_fullname(self):
        user = baker.make(settings.AUTH_USER_MODEL,
                          shortname='test@example.com',
                          fullname='')
        selector = htmls.S(devilry_listbuilder.user.ItemValue(value=user).render())
        self.assertFalse(
                selector.exists('.cradmin-legacy-listbuilder-itemvalue-titledescription-description'))

    def test_description_with_fullname(self):
        user = baker.make(settings.AUTH_USER_MODEL,
                          fullname='Test User',
                          shortname='test@example.com')
        selector = htmls.S(devilry_listbuilder.user.ItemValue(value=user).render())
        self.assertEqual(
                'test@example.com',
                selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized)
