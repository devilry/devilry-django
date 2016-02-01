import htmls
from django import test
from model_mommy import mommy

from devilry.devilry_cradmin import devilry_listbuilder


class TestItemValue(test.TestCase):
    def test_title_without_fullname(self):
        relatedstudent = mommy.make('devilry_account.PermissionGroupUser',
                                    user__shortname='test@example.com',
                                    user__fullname='')
        selector = htmls.S(devilry_listbuilder.permissiongroupuser.ItemValue(value=relatedstudent).render())
        self.assertEqual(
            'test@example.com',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_title_with_fullname(self):
        relatedstudent = mommy.make('devilry_account.PermissionGroupUser',
                                    user__fullname='Test User',
                                    user__shortname='test@example.com')
        selector = htmls.S(devilry_listbuilder.permissiongroupuser.ItemValue(value=relatedstudent).render())
        self.assertEqual(
            'Test User',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description_without_fullname(self):
        relatedstudent = mommy.make('devilry_account.PermissionGroupUser',
                                    user__shortname='test@example.com',
                                    user__fullname='')
        selector = htmls.S(devilry_listbuilder.permissiongroupuser.ItemValue(value=relatedstudent).render())
        self.assertFalse(
            selector.exists('.django-cradmin-listbuilder-itemvalue-titledescription-description'))

    def test_description_with_fullname(self):
        relatedstudent = mommy.make('devilry_account.PermissionGroupUser',
                                    user__fullname='Test User',
                                    user__shortname='test@example.com')
        selector = htmls.S(devilry_listbuilder.permissiongroupuser.ItemValue(value=relatedstudent).render())
        self.assertEqual(
            'test@example.com',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)
