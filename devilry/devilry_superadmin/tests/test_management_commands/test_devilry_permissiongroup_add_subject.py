

from django import test
from django.core import management
from django.core.management import CommandError
from model_bakery import baker

from devilry.devilry_account.models import PermissionGroup, SubjectPermissionGroup


class TestPermissionGroupAddSubjectCommand(test.TestCase):
    def __run_management_command(self, subject_short_name, group_name, *args):
        management.call_command(
            'devilry_permissiongroup_add_subject', subject_short_name, group_name)

    def test_subject_with_short_name_does_not_exist(self):
        with self.assertRaisesMessage(CommandError, 'Subject with short name "test" does not exist.'):
            self.__run_management_command('test', 'Test')

    def test_permission_group_does_not_exist(self):
        baker.make('core.Subject', short_name='test')
        with self.assertRaisesMessage(CommandError, 'PermissionGroup "Test" does not exist.'):
            self.__run_management_command('test', 'Test')

    def test_permission_group_with_type_periodadmin_error_message(self):
        baker.make('core.Subject', short_name='test')
        baker.make('devilry_account.PermissionGroup',
                   name='Test', grouptype=PermissionGroup.GROUPTYPE_PERIODADMIN)
        with self.assertRaisesMessage(CommandError, 'PermissionGroup "Test" does not exist.'):
            self.__run_management_command('test', 'Test')

    def test_subject_already_added_to_permissiongroup_error_message(self):
        subject = baker.make('core.Subject', short_name='test')
        permissiongroup = baker.make('devilry_account.PermissionGroup',
                                     name='Test', grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        baker.make('devilry_account.SubjectPermissionGroup', permissiongroup=permissiongroup, subject=subject)
        with self.assertRaisesMessage(CommandError, 'Subject already added to permission group "Test".'):
            self.__run_management_command('test', 'Test')

    def test_add_subject_to_permissiongroup_with_type_subject(self):
        baker.make('core.Subject', short_name='test')
        baker.make('devilry_account.PermissionGroup',
                   name='Test', grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        self.__run_management_command('test', 'Test')
        self.assertTrue(
            SubjectPermissionGroup.objects.filter(subject__short_name='test', permissiongroup__name='Test').exists())

    def test_add_subject_to_permissiongroup_with_type_department(self):
        baker.make('core.Subject', short_name='test')
        baker.make('devilry_account.PermissionGroup',
                   name='Test', grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
        self.__run_management_command('test', 'Test')
        self.assertTrue(
            SubjectPermissionGroup.objects.filter(subject__short_name='test', permissiongroup__name='Test').exists())

    def test_add_subject_to_multiple_permissiongroups(self):
        baker.make('core.Subject', short_name='test')
        baker.make('devilry_account.PermissionGroup',
                   name='DepartmentAdmins', grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
        baker.make('devilry_account.PermissionGroup',
                   name='SubjectAdmins', grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
        self.__run_management_command('test', 'DepartmentAdmins')
        self.__run_management_command('test', 'SubjectAdmins')
        self.assertTrue(
            SubjectPermissionGroup.objects.filter(
                subject__short_name='test', permissiongroup__name='DepartmentAdmins').exists())
        self.assertTrue(
            SubjectPermissionGroup.objects.filter(
                subject__short_name='test', permissiongroup__name='SubjectAdmins').exists())
