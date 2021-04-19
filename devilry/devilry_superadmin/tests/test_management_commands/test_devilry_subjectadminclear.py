

from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import management
from django.core.management import CommandError
from model_bakery import baker

from devilry.devilry_account.models import PermissionGroup, PermissionGroupUser, SubjectPermissionGroup


class TestSubjectadminclearCommand(test.TestCase):
    def __run_management_command(self, subject_short_name):
        management.call_command(
            'devilry_subjectadminclear',
            subject_short_name)

    def test_invalid_subject_short_name(self):
        baker.make(settings.AUTH_USER_MODEL, shortname='testuser')
        with self.assertRaisesMessage(CommandError,
                                      'Invalid subject_short_name.'):
            self.__run_management_command(subject_short_name='invalid')

    def test_ok_no_permissiongroup(self):
        baker.make('core.Subject', short_name='testsubject')
        self.assertEqual(PermissionGroup.objects.count(), 0)
        self.__run_management_command(subject_short_name='testsubject')
        self.assertEqual(PermissionGroup.objects.count(), 0)

    def test_ok_existing_permission_group(self):
        subject = baker.make('core.Subject', short_name='testsubject')
        groupname = PermissionGroup.objects.get_name_from_syncsystem(
            basenode=subject, grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        permissiongroup = baker.make(
            'devilry_account.PermissionGroup',
            name=groupname, is_custom_manageable=False,
            grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        baker.make('devilry_account.SubjectPermissionGroup',
                   permissiongroup=permissiongroup,
                   subject=subject)
        self.assertEqual(PermissionGroup.objects.count(), 1)
        self.assertEqual(SubjectPermissionGroup.objects.count(), 1)
        self.__run_management_command(subject_short_name='testsubject')
        self.assertEqual(PermissionGroup.objects.count(), 0)
        self.assertEqual(SubjectPermissionGroup.objects.count(), 0)

    def test_ok_existing_permission_group_and_permission_group_user(self):
        user = baker.make(settings.AUTH_USER_MODEL, shortname='testuser')
        subject = baker.make('core.Subject', short_name='testsubject')
        groupname = PermissionGroup.objects.get_name_from_syncsystem(
            basenode=subject, grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        permissiongroup = baker.make(
            'devilry_account.PermissionGroup',
            name=groupname, is_custom_manageable=False,
            grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        baker.make('devilry_account.PermissionGroupUser',
                   permissiongroup=permissiongroup, user=user)
        self.assertEqual(PermissionGroupUser.objects.count(), 1)
        self.__run_management_command(subject_short_name='testsubject')
        self.assertEqual(PermissionGroupUser.objects.count(), 0)
        self.assertTrue(get_user_model().objects.filter(id=user.id).exists())
