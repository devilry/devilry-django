from __future__ import unicode_literals

import mock
from django import test
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_account.models import PermissionGroupUser, PermissionGroup, PeriodPermissionGroup
from devilry.devilry_admin.views.period import admins


class TestOverview(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = admins.Overview

    def __get_titles(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.django-cradmin-listbuilder-itemvalue-titledescription-title')]

    def test_title(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertIn('Administrators for testsubject.testperiod',
                      mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual('Administrators for testsubject.testperiod',
                         mockresponse.selector.one('h1').alltext_normalized)

    def test_buttonbar_addbutton_link(self):
        testperiod = mommy.make('core.Period')
        mock_cradmin_app = mock.MagicMock()

        def mock_reverse_appurl(viewname, **kwargs):
            return '/{}'.format(viewname)

        mock_cradmin_app.reverse_appurl = mock_reverse_appurl
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod,
                                                          cradmin_app=mock_cradmin_app)
        self.assertEqual(
                '/add',
                mockresponse.selector.one('#devilry_admin_period_admins_overview_button_add')['href'])

    def test_buttonbar_addbutton_label(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'Add semester administrators',
                mockresponse.selector.one(
                        '#devilry_admin_period_admins_overview_button_add').alltext_normalized)

    def test_no_admins_messages(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'No manually added semester administrators for this semester. '
                'You can add administrators using the button above.',
                mockresponse.selector.one('.django-cradmin-listing-no-items-message').alltext_normalized)

    def test_default_ordering(self):
        testperiod = mommy.make('core.Period')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           permissiongroup__is_custom_manageable=True,
                                           period=testperiod)
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=periodpermissiongroup.permissiongroup,
                   user__shortname='userb')
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=periodpermissiongroup.permissiongroup,
                   user__shortname='usera')
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=periodpermissiongroup.permissiongroup,
                   user__shortname='userc')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(['usera', 'userb', 'userc'],
                         self.__get_titles(mockresponse.selector))

    def test_only_users_from_the_permissiongroup(self):
        testperiod = mommy.make('core.Period')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           permissiongroup__is_custom_manageable=True,
                                           period=testperiod)
        mommy.make('devilry_account.PermissionGroupUser',
                   user__shortname='userb')
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=periodpermissiongroup.permissiongroup,
                   user__shortname='usera')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(['usera'],
                         self.__get_titles(mockresponse.selector))

    def test_delete_link_label(self):
        testperiod = mommy.make('core.Period')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           permissiongroup__is_custom_manageable=True,
                                           period=testperiod)
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=periodpermissiongroup.permissiongroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'Remove',
                mockresponse.selector.one(
                        '.devilry-admin-period-admin-delete-link').alltext_normalized)

    def test_delete_arialabel(self):
        testperiod = mommy.make('core.Period')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           permissiongroup__is_custom_manageable=True,
                                           period=testperiod)
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=periodpermissiongroup.permissiongroup,
                   user__shortname='testadmin')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'Remove testadmin',
                mockresponse.selector.one(
                        '.devilry-admin-period-admin-delete-link')['aria-label'])

    def test_other_permissiongroups_heading(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'Other administrators with access to testsubject.testperiod',
                mockresponse.selector.one(
                        '#devilry_admin_period_admins_other_admins_container h2').alltext_normalized)

    def test_other_permissiongroups_no_permissiongroups(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                'No other administrators than the ones listed above have access.',
                mockresponse.selector.one(
                        '#devilry_admin_period_admins_other_admins_nonemessage').alltext_normalized)

    def test_other_permissiongroups_no_permissiongroups_except_the_custom_manageable(self):
        testperiod = mommy.make('core.Period')
        mommy.make('devilry_account.PeriodPermissionGroup',
                   permissiongroup__is_custom_manageable=True,
                   period=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertTrue(
                mockresponse.selector.exists('#devilry_admin_period_admins_other_admins_nonemessage'))

    def test_other_permissiongroups_not_permissiongroups_for_other_periods(self):
        testperiod = mommy.make('core.Period')
        otherperiod = mommy.make('core.Period')
        mommy.make('devilry_account.PeriodPermissionGroup',
                   period=otherperiod)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertTrue(
                mockresponse.selector.exists('#devilry_admin_period_admins_other_admins_nonemessage'))

    def test_other_permissiongroups_not_permissiongroups_for_other_subjects(self):
        testperiod = mommy.make('core.Period')
        othersubject = mommy.make('core.Subject')
        mommy.make('devilry_account.SubjectPermissionGroup',
                   subject=othersubject)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertTrue(
                mockresponse.selector.exists('#devilry_admin_period_admins_other_admins_nonemessage'))

    def __get_otherpermissiongroups_titles(self, selector):
        return {element.alltext_normalized
                for element in selector.list(
                    '.devilry-cradmin-subjectandperiodpermissiongroup-list '
                    '.django-cradmin-listbuilder-itemvalue-titledescription-title')}

    def test_other_permissiongroups(self):
        testperiod = mommy.make('core.Period')
        mommy.make('devilry_account.PeriodPermissionGroup',
                   period=testperiod,
                   permissiongroup__name='Other periodadmins')
        mommy.make('devilry_account.SubjectPermissionGroup',
                   subject=testperiod.subject,
                   permissiongroup__name='Other course admins')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(
                {'Other periodadmins', 'Other course admins'},
                self.__get_otherpermissiongroups_titles(mockresponse.selector))

    def test_querycount(self):
        testperiod = mommy.make('core.Period')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           permissiongroup__is_custom_manageable=True,
                                           period=testperiod)
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=periodpermissiongroup.permissiongroup,
                   _quantity=10)

        extraperiodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                                period=testperiod)
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=extraperiodpermissiongroup.permissiongroup,
                   _quantity=10)

        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            subject=testperiod.subject)
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=subjectpermissiongroup.permissiongroup,
                   _quantity=10)

        mommy.make('devilry_account.PeriodPermissionGroup',
                   period=testperiod, _quantity=10)
        mommy.make('devilry_account.SubjectPermissionGroup',
                   subject=testperiod.subject, _quantity=10)

        with self.assertNumQueries(9):
            self.mock_http200_getrequest_htmls(cradmin_role=testperiod)


class TestAddView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = admins.AddView

    def test_get_title(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         'Select the admins you want to add to testsubject.testperiod')

    def test_get_h1(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod)
        self.assertEqual(mockresponse.selector.one('h1').alltext_normalized,
                         'Select the admins you want to add to testsubject.testperiod')

    def test_render_sanity(self):
        testperiod = mommy.make('core.Period')
        mommy.make(settings.AUTH_USER_MODEL,
                   fullname='Test User',
                   shortname='test@example.com')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=mock.MagicMock(),
                                                          cradmin_role=testperiod)
        self.assertEqual(
                'Test User',
                mockresponse.selector.one(
                        '.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)
        self.assertEqual(
                'test@example.com',
                mockresponse.selector.one(
                        '.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)

    def __get_titles(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.django-cradmin-listbuilder-itemvalue-titledescription-title')]

    def test_exclude_users_in_periodpermissiongroup(self):
        testperiod = mommy.make('core.Period')
        mommy.make(settings.AUTH_USER_MODEL,
                   fullname='Not in any permissiongroup')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod)
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=periodpermissiongroup.permissiongroup,
                   user__shortname='In period permissiongroup')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=mock.MagicMock(),
                                                          cradmin_role=testperiod)
        self.assertEqual(
                {'Not in any permissiongroup'},
                set(self.__get_titles(mockresponse.selector)))

    def test_include_users_in_other_periodpermissiongroup(self):
        testperiod = mommy.make('core.Period')
        otherperiod = mommy.make('core.Period')
        otherperiodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                                period=otherperiod)
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=otherperiodpermissiongroup.permissiongroup,
                   user__shortname='In other period permissiongroup')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=mock.MagicMock(),
                                                          cradmin_role=testperiod)
        self.assertEqual(
                {'In other period permissiongroup'},
                set(self.__get_titles(mockresponse.selector)))

    def test_exclude_users_in_subjectpermissiongroup(self):
        testperiod = mommy.make('core.Period')
        mommy.make(settings.AUTH_USER_MODEL,
                   fullname='Not in any permissiongroup')
        subjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                            subject=testperiod.subject)
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=subjectpermissiongroup.permissiongroup,
                   user__shortname='In period permissiongroup')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=mock.MagicMock(),
                                                          cradmin_role=testperiod)
        self.assertEqual(
                {'Not in any permissiongroup'},
                set(self.__get_titles(mockresponse.selector)))

    def test_include_users_in_other_subjectpermissiongroup(self):
        testperiod = mommy.make('core.Period')
        otherperiod = mommy.make('core.Period')
        othersubjectpermissiongroup = mommy.make('devilry_account.SubjectPermissionGroup',
                                                 subject=otherperiod.subject)
        mommy.make('devilry_account.PermissionGroupUser',
                   permissiongroup=othersubjectpermissiongroup.permissiongroup,
                   user__shortname='In other subject permissiongroup')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=mock.MagicMock(),
                                                          cradmin_role=testperiod)
        self.assertEqual(
                {'In other subject permissiongroup'},
                set(self.__get_titles(mockresponse.selector)))

    def test_post_creates_permissiongroup_if_it_does_not_exist(self):
        testperiod = mommy.make('core.Period')
        adminuser = mommy.make(settings.AUTH_USER_MODEL)
        self.assertEqual(0, PermissionGroup.objects.count())
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestkwargs={
                    'data': {
                        'selected_items': [str(adminuser.id)]
                    }
                })
        self.assertEqual(1, PermissionGroup.objects.count())
        created_permissiongroup = PermissionGroup.objects.first()
        self.assertEqual('Custom manageable permissiongroup for Period#{}'.format(testperiod.id),
                         created_permissiongroup.name)
        self.assertEqual(PermissionGroup.GROUPTYPE_PERIODADMIN, created_permissiongroup.grouptype)
        self.assertTrue(created_permissiongroup.is_custom_manageable)
        created_periodpermissiongroup = PeriodPermissionGroup.objects.first()
        self.assertEqual(created_permissiongroup, created_periodpermissiongroup.permissiongroup)
        self.assertEqual(testperiod, created_periodpermissiongroup.period)

    def test_post_creates_permissiongroup_if_non_custom_managable_permissiongroup_exists(self):
        testperiod = mommy.make('core.Period')
        mommy.make('devilry_account.PeriodPermissionGroup',
                   period=testperiod,
                   permissiongroup__is_custom_manageable=False)
        adminuser = mommy.make(settings.AUTH_USER_MODEL)
        self.assertEqual(1, PermissionGroup.objects.count())
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestkwargs={
                    'data': {
                        'selected_items': [str(adminuser.id)]
                    }
                })
        self.assertEqual(2, PermissionGroup.objects.count())

    def test_post_does_not_create_permissiongroup_if_it_exist(self):
        testperiod = mommy.make('core.Period')
        mommy.make('devilry_account.PeriodPermissionGroup',
                   period=testperiod,
                   permissiongroup__is_custom_manageable=True)
        adminuser = mommy.make(settings.AUTH_USER_MODEL)
        self.assertEqual(1, PermissionGroup.objects.count())
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestkwargs={
                    'data': {
                        'selected_items': [str(adminuser.id)]
                    }
                })
        self.assertEqual(1, PermissionGroup.objects.count())

    def test_post_creates_permissiongroupuser(self):
        testperiod = mommy.make('core.Period')
        adminuser = mommy.make(settings.AUTH_USER_MODEL)
        self.assertEqual(0, PermissionGroupUser.objects.count())
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestkwargs={
                    'data': {
                        'selected_items': [str(adminuser.id)]
                    }
                })
        self.assertEqual(1, PermissionGroupUser.objects.count())
        created_permissiongroupuser = PermissionGroupUser.objects.first()
        self.assertEqual(adminuser, created_permissiongroupuser.user)
        self.assertEqual(
                testperiod,
                created_permissiongroupuser.permissiongroup.periodpermissiongroup_set.first().period)

    def test_post_multiple_users(self):
        testperiod = mommy.make('core.Period')
        adminuser1 = mommy.make(settings.AUTH_USER_MODEL)
        adminuser2 = mommy.make(settings.AUTH_USER_MODEL)
        adminuser3 = mommy.make(settings.AUTH_USER_MODEL)
        self.assertEqual(0, PermissionGroupUser.objects.count())
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                requestkwargs={
                    'data': {
                        'selected_items': [str(adminuser1.id),
                                           str(adminuser2.id),
                                           str(adminuser3.id)]
                    }
                })
        self.assertEqual(3, PermissionGroupUser.objects.count())

    def test_post_success_message(self):
        testperiod = mommy.make('core.Period')
        adminuser1 = mommy.make(settings.AUTH_USER_MODEL,
                                shortname='testuser')
        adminuser2 = mommy.make(settings.AUTH_USER_MODEL,
                                fullname='Test User')
        self.assertEqual(0, PermissionGroupUser.objects.count())
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                requestkwargs={
                    'data': {
                        'selected_items': [str(adminuser1.id),
                                           str(adminuser2.id)]
                    }
                })
        messagesmock.add.assert_called_once_with(
                messages.SUCCESS,
                'Added "Test User", "testuser".',
                '')


class TestDeleteView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = admins.DeleteView

    def test_get_title(self):
        testperiod = mommy.make('core.Period')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod,
                                           permissiongroup__is_custom_manageable=True)
        permissiongroupuser = mommy.make('devilry_account.PermissionGroupUser',
                                         permissiongroup=periodpermissiongroup.permissiongroup,
                                         user__fullname='Awesome Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={'pk': permissiongroupuser.pk})
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         'Remove semester administrator: Awesome Doe?')

    def test_get_h1(self):
        testperiod = mommy.make('core.Period')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod,
                                           permissiongroup__is_custom_manageable=True)
        permissiongroupuser = mommy.make('devilry_account.PermissionGroupUser',
                                         permissiongroup=periodpermissiongroup.permissiongroup,
                                         user__fullname='Awesome Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={'pk': permissiongroupuser.pk})
        self.assertEqual(mockresponse.selector.one('h1').alltext_normalized,
                         'Remove semester administrator: Awesome Doe?')

    def test_get_confirm_message(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod,
                                           permissiongroup__is_custom_manageable=True)
        permissiongroupuser = mommy.make('devilry_account.PermissionGroupUser',
                                         permissiongroup=periodpermissiongroup.permissiongroup,
                                         user__fullname='Awesome Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testperiod,
                viewkwargs={'pk': permissiongroupuser.pk})
        self.assertEqual(mockresponse.selector.one('.devilry-cradmin-confirmview-message').alltext_normalized,
                         'Are you sure you want to remove Awesome Doe as semester administrator '
                         'for testsubject.testperiod? You can re-add a removed administrator at any time.')

    def test_404_if_no_custom_managable_permissiongroup_for_period(self):
        testperiod = mommy.make('core.Period')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod,
                                           permissiongroup__is_custom_manageable=False)
        permissiongroupuser = mommy.make('devilry_account.PermissionGroupUser',
                                         permissiongroup=periodpermissiongroup.permissiongroup)
        with self.assertRaisesMessage(
                Http404,
                'No custom managable permissiongroup for Period#{} found.'.format(
                        testperiod.id)):
            self.mock_getrequest(
                    cradmin_role=testperiod,
                    viewkwargs={'pk': permissiongroupuser.pk})

    def test_404_if_not_in_correct_custom_managable_permissiongroup(self):
        otherperiod = mommy.make('core.Period')
        otherperiodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                                period=otherperiod,
                                                permissiongroup__is_custom_manageable=True)
        permissiongroupuser = mommy.make('devilry_account.PermissionGroupUser',
                                         permissiongroup=otherperiodpermissiongroup.permissiongroup)
        testperiod = mommy.make('core.Period')
        mommy.make('devilry_account.PeriodPermissionGroup',
                   period=testperiod,
                   permissiongroup__is_custom_manageable=True)
        with self.assertRaisesMessage(
                Http404,
                'No PermissionGroupUser in custom managable '
                'permissiongroup for Period#{} found.'.format(testperiod.id)):
            self.mock_getrequest(
                    cradmin_role=testperiod,
                    viewkwargs={'pk': permissiongroupuser.pk})

    def test_404_if_not_in_custom_managable_permissiongroup_for_period(self):
        testperiod = mommy.make('core.Period')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod,
                                           permissiongroup__is_custom_manageable=False)
        permissiongroupuser = mommy.make('devilry_account.PermissionGroupUser',
                                         permissiongroup=periodpermissiongroup.permissiongroup)
        mommy.make('devilry_account.PeriodPermissionGroup',
                   period=testperiod,
                   permissiongroup__is_custom_manageable=True)
        with self.assertRaisesMessage(
                Http404,
                'No PermissionGroupUser in custom managable '
                'permissiongroup for Period#{} found.'.format(testperiod.id)):
            self.mock_getrequest(
                    cradmin_role=testperiod,
                    viewkwargs={'pk': permissiongroupuser.pk})

    def test_post_deletes_permissiongroupuser(self):
        testperiod = mommy.make('core.Period')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod,
                                           permissiongroup__is_custom_manageable=True)
        permissiongroupuser = mommy.make('devilry_account.PermissionGroupUser',
                                         permissiongroup=periodpermissiongroup.permissiongroup)
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                viewkwargs={'pk': permissiongroupuser.pk})
        self.assertFalse(PermissionGroupUser.objects.filter(id=permissiongroupuser.id).exists())

    def test_post_success_message(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        periodpermissiongroup = mommy.make('devilry_account.PeriodPermissionGroup',
                                           period=testperiod,
                                           permissiongroup__is_custom_manageable=True)
        permissiongroupuser = mommy.make('devilry_account.PermissionGroupUser',
                                         permissiongroup=periodpermissiongroup.permissiongroup,
                                         user__fullname='Awesome Doe')
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
                cradmin_role=testperiod,
                messagesmock=messagesmock,
                viewkwargs={'pk': permissiongroupuser.pk})
        messagesmock.add.assert_called_once_with(
                messages.SUCCESS,
                'Awesome Doe is no longer semester administrator for testsubject.testperiod.',
                '')
