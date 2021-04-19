import htmls
from django import test
from model_bakery import baker

from devilry.devilry_cradmin import devilry_listbuilder


class TestItemValue(test.TestCase):
    def test_title_without_fullname(self):
        relatedstudent = baker.make('devilry_account.PermissionGroupUser',
                                    user__shortname='test@example.com',
                                    user__fullname='')
        selector = htmls.S(devilry_listbuilder.permissiongroupuser.ItemValue(value=relatedstudent).render())
        self.assertEqual(
            'test@example.com',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_title_with_fullname(self):
        relatedstudent = baker.make('devilry_account.PermissionGroupUser',
                                    user__fullname='Test User',
                                    user__shortname='test@example.com')
        selector = htmls.S(devilry_listbuilder.permissiongroupuser.ItemValue(value=relatedstudent).render())
        self.assertEqual(
            'Test User',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description_without_fullname(self):
        relatedstudent = baker.make('devilry_account.PermissionGroupUser',
                                    user__shortname='test@example.com',
                                    user__fullname='')
        selector = htmls.S(devilry_listbuilder.permissiongroupuser.ItemValue(value=relatedstudent).render())
        self.assertFalse(
            selector.exists('.cradmin-legacy-listbuilder-itemvalue-titledescription-description'))

    def test_description_with_fullname(self):
        relatedstudent = baker.make('devilry_account.PermissionGroupUser',
                                    user__fullname='Test User',
                                    user__shortname='test@example.com')
        selector = htmls.S(devilry_listbuilder.permissiongroupuser.ItemValue(value=relatedstudent).render())
        self.assertEqual(
            'test@example.com',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized)
