

import mock
from django import test
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.devilry_account.models import PermissionGroupUser, PermissionGroup, SubjectPermissionGroup
from devilry.devilry_admin.views.subject import admins


class TestOverview(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = admins.Overview

    def __get_titles(self, selector):
        return [element.alltext_normalized
                for element in selector.list('.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]

    def test_title(self):
        testsubject = baker.make('core.Subject',
                                 short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertIn('Administrators for testsubject',
                      mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testsubject = baker.make('core.Subject',
                                 short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual('Administrators for testsubject',
                         mockresponse.selector.one('h1').alltext_normalized)

    def test_buttonbar_addbutton_link(self):
        testsubject = baker.make('core.Subject')
        mock_cradmin_app = mock.MagicMock()

        def mock_reverse_appurl(viewname, **kwargs):
            return '/{}'.format(viewname)

        mock_cradmin_app.reverse_appurl = mock_reverse_appurl
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject,
                                                          cradmin_app=mock_cradmin_app)
        self.assertEqual(
                '/add',
                mockresponse.selector.one('#devilry_admin_subject_admins_overview_button_add')['href'])

    def test_buttonbar_addbutton_label(self):
        testsubject = baker.make('core.Subject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual(
                'Add course administrators',
                mockresponse.selector.one(
                        '#devilry_admin_subject_admins_overview_button_add').alltext_normalized)

    def test_no_admins_messages(self):
        testsubject = baker.make('core.Subject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual(
                'No manually added course administrators for this course. '
                'You can add administrators using the button above.',
                mockresponse.selector.one('.cradmin-legacy-listing-no-items-message').alltext_normalized)

    def test_default_ordering(self):
        testsubject = baker.make('core.Subject')
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            permissiongroup__is_custom_manageable=True,
                                            subject=testsubject)
        baker.make('devilry_account.PermissionGroupUser',
                   permissiongroup=subjectpermissiongroup.permissiongroup,
                   user__shortname='userb')
        baker.make('devilry_account.PermissionGroupUser',
                   permissiongroup=subjectpermissiongroup.permissiongroup,
                   user__shortname='usera')
        baker.make('devilry_account.PermissionGroupUser',
                   permissiongroup=subjectpermissiongroup.permissiongroup,
                   user__shortname='userc')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual(['usera', 'userb', 'userc'],
                         self.__get_titles(mockresponse.selector))

    def test_only_users_from_the_permissiongroup(self):
        testsubject = baker.make('core.Subject')
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            permissiongroup__is_custom_manageable=True,
                                            subject=testsubject)
        baker.make('devilry_account.PermissionGroupUser',
                   user__shortname='userb')
        baker.make('devilry_account.PermissionGroupUser',
                   permissiongroup=subjectpermissiongroup.permissiongroup,
                   user__shortname='usera')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual(['usera'],
                         self.__get_titles(mockresponse.selector))

    def test_delete_link_label(self):
        testsubject = baker.make('core.Subject')
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            permissiongroup__is_custom_manageable=True,
                                            subject=testsubject)
        baker.make('devilry_account.PermissionGroupUser',
                   permissiongroup=subjectpermissiongroup.permissiongroup)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual(
                'Remove',
                mockresponse.selector.one(
                        '.devilry-admin-subject-admin-delete-link').alltext_normalized)

    def test_delete_arialabel(self):
        testsubject = baker.make('core.Subject')
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            permissiongroup__is_custom_manageable=True,
                                            subject=testsubject)
        baker.make('devilry_account.PermissionGroupUser',
                   permissiongroup=subjectpermissiongroup.permissiongroup,
                   user__shortname='testadmin')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual(
                'Remove testadmin',
                mockresponse.selector.one(
                        '.devilry-admin-subject-admin-delete-link')['aria-label'])

    def test_other_permissiongroups_heading(self):
        testsubject = baker.make('core.Subject',
                                 short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual(
                'Other administrators with access to testsubject',
                mockresponse.selector.one(
                        '#devilry_admin_subject_admins_other_admins_container h2').alltext_normalized)

    def test_other_permissiongroups_no_permissiongroups(self):
        testsubject = baker.make('core.Subject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual(
                'No other administrators than the ones listed above have access.',
                mockresponse.selector.one(
                        '#devilry_admin_subject_admins_other_admins_nonemessage').alltext_normalized)

    def test_other_permissiongroups_no_permissiongroups_except_the_custom_manageable(self):
        testsubject = baker.make('core.Subject')
        baker.make('devilry_account.SubjectPermissionGroup',
                   permissiongroup__is_custom_manageable=True,
                   subject=testsubject)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertTrue(
                mockresponse.selector.exists('#devilry_admin_subject_admins_other_admins_nonemessage'))

    def test_other_permissiongroups_not_permissiongroups_for_other_subjects(self):
        testsubject = baker.make('core.Subject')
        othersubject = baker.make('core.Subject')
        baker.make('devilry_account.SubjectPermissionGroup',
                   subject=othersubject)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertTrue(
                mockresponse.selector.exists('#devilry_admin_subject_admins_other_admins_nonemessage'))

    def __get_otherpermissiongroups_titles(self, selector):
        return {
            element.alltext_normalized
            for element in selector.list(
                '.devilry-cradmin-subjectandperiodpermissiongroup-list '
                '.cradmin-legacy-listbuilder-itemvalue-titledescription-title')}

    def test_other_permissiongroups(self):
        testsubject = baker.make('core.Subject')
        baker.make('devilry_account.SubjectPermissionGroup',
                   subject=testsubject,
                   permissiongroup__name='Other subjectadmins')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testsubject)
        self.assertEqual(
                {'Other subjectadmins'},
                self.__get_otherpermissiongroups_titles(mockresponse.selector))

    def test_querycount(self):
        testsubject = baker.make('core.Subject')
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            permissiongroup__is_custom_manageable=True,
                                            subject=testsubject)
        baker.make('devilry_account.PermissionGroupUser',
                   permissiongroup=subjectpermissiongroup.permissiongroup,
                   _quantity=10)

        extrasubjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                                 subject=testsubject)
        baker.make('devilry_account.PermissionGroupUser',
                   permissiongroup=extrasubjectpermissiongroup.permissiongroup,
                   _quantity=10)

        baker.make('devilry_account.SubjectPermissionGroup',
                   subject=testsubject, _quantity=10)
        baker.make('devilry_account.SubjectPermissionGroup',
                   subject=testsubject, _quantity=10)

        with self.assertNumQueries(6):
            self.mock_http200_getrequest_htmls(cradmin_role=testsubject)


class TestAddView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = admins.AddView

    def test_get_title(self):
        testsubject = baker.make('core.Subject',
                                 short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testsubject)
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         'Select the admins you want to add to testsubject')

    def test_get_h1(self):
        testsubject = baker.make('core.Subject',
                                 short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testsubject)
        self.assertEqual(mockresponse.selector.one('h1').alltext_normalized,
                         'Select the admins you want to add to testsubject')

    def test_render_sanity(self):
        testsubject = baker.make('core.Subject')
        baker.make(settings.AUTH_USER_MODEL,
                   fullname='Test User',
                   shortname='test@example.com')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=mock.MagicMock(),
                                                          cradmin_role=testsubject)
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

    def test_exclude_users_in_subjectpermissiongroup(self):
        testsubject = baker.make('core.Subject')
        baker.make(settings.AUTH_USER_MODEL,
                   fullname='Not in any permissiongroup')
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject)
        baker.make('devilry_account.PermissionGroupUser',
                   permissiongroup=subjectpermissiongroup.permissiongroup,
                   user__shortname='In subject permissiongroup')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=mock.MagicMock(),
                                                          cradmin_role=testsubject)
        self.assertEqual(
                {'Not in any permissiongroup'},
                set(self.__get_titles(mockresponse.selector)))

    def test_include_users_in_other_subjectpermissiongroup(self):
        testsubject = baker.make('core.Subject')
        othersubject = baker.make('core.Subject')
        othersubjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                                 subject=othersubject)
        baker.make('devilry_account.PermissionGroupUser',
                   permissiongroup=othersubjectpermissiongroup.permissiongroup,
                   user__shortname='In other subject permissiongroup')
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=mock.MagicMock(),
                                                          cradmin_role=testsubject)
        self.assertEqual(
                {'In other subject permissiongroup'},
                set(self.__get_titles(mockresponse.selector)))

    def test_post_creates_permissiongroup_if_it_does_not_exist(self):
        testsubject = baker.make('core.Subject')
        adminuser = baker.make(settings.AUTH_USER_MODEL)
        self.assertEqual(0, PermissionGroup.objects.count())
        self.mock_http302_postrequest(
                cradmin_role=testsubject,
                requestkwargs={
                    'data': {
                        'selected_items': [str(adminuser.id)]
                    }
                })
        self.assertEqual(1, PermissionGroup.objects.count())
        created_permissiongroup = PermissionGroup.objects.first()
        self.assertEqual('Custom manageable permissiongroup for Subject#{}'.format(testsubject.id),
                         created_permissiongroup.name)
        self.assertEqual(PermissionGroup.GROUPTYPE_SUBJECTADMIN, created_permissiongroup.grouptype)
        self.assertTrue(created_permissiongroup.is_custom_manageable)
        created_subjectpermissiongroup = SubjectPermissionGroup.objects.first()
        self.assertEqual(created_permissiongroup, created_subjectpermissiongroup.permissiongroup)
        self.assertEqual(testsubject, created_subjectpermissiongroup.subject)

    def test_post_creates_permissiongroup_if_non_custom_managable_permissiongroup_exists(self):
        testsubject = baker.make('core.Subject')
        baker.make('devilry_account.SubjectPermissionGroup',
                   subject=testsubject,
                   permissiongroup__is_custom_manageable=False)
        adminuser = baker.make(settings.AUTH_USER_MODEL)
        self.assertEqual(1, PermissionGroup.objects.count())
        self.mock_http302_postrequest(
                cradmin_role=testsubject,
                requestkwargs={
                    'data': {
                        'selected_items': [str(adminuser.id)]
                    }
                })
        self.assertEqual(2, PermissionGroup.objects.count())

    def test_post_does_not_create_permissiongroup_if_it_exist(self):
        testsubject = baker.make('core.Subject')
        baker.make('devilry_account.SubjectPermissionGroup',
                   subject=testsubject,
                   permissiongroup__is_custom_manageable=True)
        adminuser = baker.make(settings.AUTH_USER_MODEL)
        self.assertEqual(1, PermissionGroup.objects.count())
        self.mock_http302_postrequest(
                cradmin_role=testsubject,
                requestkwargs={
                    'data': {
                        'selected_items': [str(adminuser.id)]
                    }
                })
        self.assertEqual(1, PermissionGroup.objects.count())

    def test_post_creates_permissiongroupuser(self):
        testsubject = baker.make('core.Subject')
        adminuser = baker.make(settings.AUTH_USER_MODEL)
        self.assertEqual(0, PermissionGroupUser.objects.count())
        self.mock_http302_postrequest(
                cradmin_role=testsubject,
                requestkwargs={
                    'data': {
                        'selected_items': [str(adminuser.id)]
                    }
                })
        self.assertEqual(1, PermissionGroupUser.objects.count())
        created_permissiongroupuser = PermissionGroupUser.objects.first()
        self.assertEqual(adminuser, created_permissiongroupuser.user)
        self.assertEqual(
                testsubject,
                created_permissiongroupuser.permissiongroup.subjectpermissiongroup_set.first().subject)

    def test_post_multiple_users(self):
        testsubject = baker.make('core.Subject')
        adminuser1 = baker.make(settings.AUTH_USER_MODEL)
        adminuser2 = baker.make(settings.AUTH_USER_MODEL)
        adminuser3 = baker.make(settings.AUTH_USER_MODEL)
        self.assertEqual(0, PermissionGroupUser.objects.count())
        self.mock_http302_postrequest(
                cradmin_role=testsubject,
                requestkwargs={
                    'data': {
                        'selected_items': [str(adminuser1.id),
                                           str(adminuser2.id),
                                           str(adminuser3.id)]
                    }
                })
        self.assertEqual(3, PermissionGroupUser.objects.count())

    def test_post_success_message(self):
        testsubject = baker.make('core.Subject')
        adminuser1 = baker.make(settings.AUTH_USER_MODEL,
                                shortname='testuser')
        adminuser2 = baker.make(settings.AUTH_USER_MODEL,
                                fullname='Test User')
        self.assertEqual(0, PermissionGroupUser.objects.count())
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
                cradmin_role=testsubject,
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
        testsubject = baker.make('core.Subject')
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject,
                                            permissiongroup__is_custom_manageable=True)
        permissiongroupuser = baker.make('devilry_account.PermissionGroupUser',
                                         permissiongroup=subjectpermissiongroup.permissiongroup,
                                         user__fullname='Awesome Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testsubject,
                viewkwargs={'pk': permissiongroupuser.pk})
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized,
                         'Remove course administrator: Awesome Doe?')

    def test_get_h1(self):
        testsubject = baker.make('core.Subject')
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject,
                                            permissiongroup__is_custom_manageable=True)
        permissiongroupuser = baker.make('devilry_account.PermissionGroupUser',
                                         permissiongroup=subjectpermissiongroup.permissiongroup,
                                         user__fullname='Awesome Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testsubject,
                viewkwargs={'pk': permissiongroupuser.pk})
        self.assertEqual(mockresponse.selector.one('h1').alltext_normalized,
                         'Remove course administrator: Awesome Doe?')

    def test_get_confirm_message(self):
        testsubject = baker.make('core.Subject',
                                 short_name='testsubject')
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject,
                                            permissiongroup__is_custom_manageable=True)
        permissiongroupuser = baker.make('devilry_account.PermissionGroupUser',
                                         permissiongroup=subjectpermissiongroup.permissiongroup,
                                         user__fullname='Awesome Doe')
        mockresponse = self.mock_http200_getrequest_htmls(
                cradmin_role=testsubject,
                viewkwargs={'pk': permissiongroupuser.pk})
        self.assertEqual(mockresponse.selector.one('.devilry-cradmin-confirmview-message').alltext_normalized,
                         'Are you sure you want to remove Awesome Doe as course administrator '
                         'for testsubject? You can re-add a removed administrator at any time.')

    def test_404_if_no_custom_managable_permissiongroup_for_subject(self):
        testsubject = baker.make('core.Subject')
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject,
                                            permissiongroup__is_custom_manageable=False)
        permissiongroupuser = baker.make('devilry_account.PermissionGroupUser',
                                         permissiongroup=subjectpermissiongroup.permissiongroup)
        with self.assertRaisesMessage(
                Http404,
                'No custom managable permissiongroup for Subject#{} found.'.format(
                        testsubject.id)):
            self.mock_getrequest(
                    cradmin_role=testsubject,
                    viewkwargs={'pk': permissiongroupuser.pk})

    def test_404_if_not_in_correct_custom_managable_permissiongroup(self):
        othersubject = baker.make('core.Subject')
        othersubjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                                 subject=othersubject,
                                                 permissiongroup__is_custom_manageable=True)
        permissiongroupuser = baker.make('devilry_account.PermissionGroupUser',
                                         permissiongroup=othersubjectpermissiongroup.permissiongroup)
        testsubject = baker.make('core.Subject')
        baker.make('devilry_account.SubjectPermissionGroup',
                   subject=testsubject,
                   permissiongroup__is_custom_manageable=True)
        with self.assertRaisesMessage(
                Http404,
                'No PermissionGroupUser in custom managable '
                'permissiongroup for Subject#{} found.'.format(testsubject.id)):
            self.mock_getrequest(
                    cradmin_role=testsubject,
                    viewkwargs={'pk': permissiongroupuser.pk})

    def test_404_if_not_in_custom_managable_permissiongroup_for_subject(self):
        testsubject = baker.make('core.Subject')
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject,
                                            permissiongroup__is_custom_manageable=False)
        permissiongroupuser = baker.make('devilry_account.PermissionGroupUser',
                                         permissiongroup=subjectpermissiongroup.permissiongroup)
        baker.make('devilry_account.SubjectPermissionGroup',
                   subject=testsubject,
                   permissiongroup__is_custom_manageable=True)
        with self.assertRaisesMessage(
                Http404,
                'No PermissionGroupUser in custom managable '
                'permissiongroup for Subject#{} found.'.format(testsubject.id)):
            self.mock_getrequest(
                    cradmin_role=testsubject,
                    viewkwargs={'pk': permissiongroupuser.pk})

    def test_post_deletes_permissiongroupuser(self):
        testsubject = baker.make('core.Subject')
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject,
                                            permissiongroup__is_custom_manageable=True)
        permissiongroupuser = baker.make('devilry_account.PermissionGroupUser',
                                         permissiongroup=subjectpermissiongroup.permissiongroup)
        self.mock_http302_postrequest(
                cradmin_role=testsubject,
                viewkwargs={'pk': permissiongroupuser.pk})
        self.assertFalse(PermissionGroupUser.objects.filter(id=permissiongroupuser.id).exists())

    def test_post_success_message(self):
        testsubject = baker.make('core.Subject',
                                 short_name='testsubject')
        subjectpermissiongroup = baker.make('devilry_account.SubjectPermissionGroup',
                                            subject=testsubject,
                                            permissiongroup__is_custom_manageable=True)
        permissiongroupuser = baker.make('devilry_account.PermissionGroupUser',
                                         permissiongroup=subjectpermissiongroup.permissiongroup,
                                         user__fullname='Awesome Doe')
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
                cradmin_role=testsubject,
                messagesmock=messagesmock,
                viewkwargs={'pk': permissiongroupuser.pk})
        messagesmock.add.assert_called_once_with(
                messages.SUCCESS,
                'Awesome Doe is no longer course administrator for testsubject.',
                '')
