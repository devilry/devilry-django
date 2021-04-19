

from django import test
from django.conf import settings
from django.core import management
from django.core.management import CommandError
from model_bakery import baker

from devilry.devilry_account.models import PermissionGroup, PermissionGroupUser, SubjectPermissionGroup


class TestSubjectadminaddCommand(test.TestCase):
    def __run_management_command(self, subject_short_name, user_shortname):
        management.call_command(
            'devilry_subjectadminadd',
            subject_short_name, user_shortname)

    def test_invalid_subject_short_name(self):
        baker.make(settings.AUTH_USER_MODEL, shortname='testuser')
        with self.assertRaisesMessage(CommandError,
                                      'Invalid subject_short_name.'):
            self.__run_management_command(subject_short_name='invalid',
                                          user_shortname='testuser')

    def test_invalid_user_shortname(self):
        baker.make('core.Subject', short_name='testsubject')
        with self.assertRaisesMessage(CommandError,
                                      'Invalid user_shortname.'):
            self.__run_management_command(subject_short_name='testsubject',
                                          user_shortname='invalid')

    def test_ok_new_permission_group(self):
        user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser')
        subject = baker.make('core.Subject', short_name='testsubject')
        self.__run_management_command(subject_short_name='testsubject',
                                      user_shortname='testuser')
        expected_groupname = PermissionGroup.objects.get_name_from_syncsystem(
            basenode=subject, grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)

        self.assertEqual(PermissionGroup.objects.count(), 1)
        created_permissiongroup = PermissionGroup.objects.first()
        self.assertFalse(created_permissiongroup.is_custom_manageable)
        self.assertEqual(created_permissiongroup.name, expected_groupname)

        self.assertEqual(SubjectPermissionGroup.objects.count(), 1)
        created_subject_permissiongroup = SubjectPermissionGroup.objects.first()
        self.assertEqual(created_subject_permissiongroup.permissiongroup,
                         created_permissiongroup)

        self.assertEqual(PermissionGroupUser.objects.count(), 1)
        created_permissiongroupuser = PermissionGroupUser.objects.first()
        self.assertEqual(created_permissiongroupuser.user, user)

    def test_ok_existing_permission_group(self):
        user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser')
        subject = baker.make('core.Subject', short_name='testsubject')
        groupname = PermissionGroup.objects.get_name_from_syncsystem(
            basenode=subject, grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        baker.make('devilry_account.PermissionGroup',
                   name=groupname, is_custom_manageable=False,
                   grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        self.__run_management_command(subject_short_name='testsubject',
                                      user_shortname='testuser')
        self.assertEqual(PermissionGroup.objects.count(), 1)
        updated_permissiongroup = PermissionGroup.objects.first()
        self.assertFalse(updated_permissiongroup.is_custom_manageable)
        self.assertEqual(updated_permissiongroup.name, groupname)

        self.assertEqual(PermissionGroupUser.objects.count(), 1)
        created_permissiongroupuser = PermissionGroupUser.objects.first()
        self.assertEqual(created_permissiongroupuser.user, user)

    def test_ok_existing_permission_group_and_permission_group_user(self):
        user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser')
        subject = baker.make('core.Subject', short_name='testsubject')
        groupname = PermissionGroup.objects.get_name_from_syncsystem(
            basenode=subject, grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        permissiongroup = baker.make('devilry_account.PermissionGroup',
                                     name=groupname, is_custom_manageable=False,
                                     grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        baker.make('devilry_account.PermissionGroupUser',
                   permissiongroup=permissiongroup, user=user)
        self.__run_management_command(subject_short_name='testsubject',
                                      user_shortname='testuser')
        self.assertEqual(PermissionGroup.objects.count(), 1)
        updated_permissiongroup = PermissionGroup.objects.first()
        self.assertFalse(updated_permissiongroup.is_custom_manageable)
        self.assertEqual(updated_permissiongroup.name, groupname)

        self.assertEqual(PermissionGroupUser.objects.count(), 1)
        created_permissiongroupuser = PermissionGroupUser.objects.first()
        self.assertEqual(created_permissiongroupuser.user, user)
