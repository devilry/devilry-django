import htmls
from django import test
from model_mommy import mommy

from devilry.devilry_cradmin import devilry_listbuilder


class TestSubjectPermissionGroupItemValue(test.TestCase):
    def test_title_is_custom_manageable_false(self):
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            permissiongroup__is_custom_manageable=False,
                                            permissiongroup__name='Test subject permission group')
        selector = htmls.S(devilry_listbuilder.permissiongroup.SubjectPermissionGroupItemValue(
                value=subjectpermissiongroup).render())
        self.assertEqual(
                'Test subject permission group',
                selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_title_is_custom_manageable_true(self):
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            permissiongroup__is_custom_manageable=True,
                                            subject__short_name='testsubject')
        selector = htmls.S(devilry_listbuilder.permissiongroup.SubjectPermissionGroupItemValue(
                value=subjectpermissiongroup).render())
        self.assertEqual(
                'Course administrators for testsubject',
                selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_get_description_no_users(self):
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup')
        selector = htmls.S(devilry_listbuilder.permissiongroup.SubjectPermissionGroupItemValue(
                value=subjectpermissiongroup).render())
        self.assertEqual(
                'No users in permission group',
                selector.one('.devilry-cradmin-subjectorperiodpermissiongroup-nouserswarning').alltext_normalized)

    def __get_user_names(self, selector):
        return {element.alltext_normalized
                for element in selector.list('.devilry-user-verbose-inline')}

    def test_get_description_with_users(self):
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup')
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=subjectpermissiongroup.permissiongroup,
                   user__shortname='usera')
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=subjectpermissiongroup.permissiongroup,
                   user__fullname='User B',
                   user__shortname='userb')
        selector = htmls.S(devilry_listbuilder.permissiongroup.SubjectPermissionGroupItemValue(
                value=subjectpermissiongroup).render())
        self.assertFalse(selector.exists('.devilry-cradmin-subjectorperiodpermissiongroup-nouserswarning'))
        self.assertEqual(
                {'usera', 'User B(userb)'},
                self.__get_user_names(selector))


class TestPeriodPermissionGroupItemValue(test.TestCase):
    def test_title_is_custom_manageable_false(self):
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           permissiongroup__is_custom_manageable=False,
                                           permissiongroup__name='Test period permission group')
        selector = htmls.S(devilry_listbuilder.permissiongroup.PeriodPermissionGroupItemValue(
                value=periodpermissiongroup).render())
        self.assertEqual(
                'Test period permission group',
                selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_title_is_custom_manageable_true(self):
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           permissiongroup__is_custom_manageable=True,
                                           period__parentnode__short_name='testsubject',
                                           period__short_name='testperiod')
        selector = htmls.S(devilry_listbuilder.permissiongroup.PeriodPermissionGroupItemValue(
                value=periodpermissiongroup).render())
        self.assertEqual(
                'Semester administrators for testsubject.testperiod',
                selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_get_description_no_users(self):
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup')
        selector = htmls.S(devilry_listbuilder.permissiongroup.PeriodPermissionGroupItemValue(
                value=periodpermissiongroup).render())
        self.assertEqual(
                'No users in permission group',
                selector.one('.devilry-cradmin-subjectorperiodpermissiongroup-nouserswarning').alltext_normalized)

    def __get_user_names(self, selector):
        return {element.alltext_normalized
                for element in selector.list('.devilry-user-verbose-inline')}

    def test_get_description_with_users(self):
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup')
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=periodpermissiongroup.permissiongroup,
                   user__shortname='usera')
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=periodpermissiongroup.permissiongroup,
                   user__fullname='User B',
                   user__shortname='userb')
        selector = htmls.S(devilry_listbuilder.permissiongroup.PeriodPermissionGroupItemValue(
                value=periodpermissiongroup).render())
        self.assertFalse(selector.exists('.devilry-cradmin-subjectorperiodpermissiongroup-nouserswarning'))
        self.assertEqual(
                {'usera', 'User B(userb)'},
                self.__get_user_names(selector))
