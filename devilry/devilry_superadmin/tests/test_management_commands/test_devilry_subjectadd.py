

from django import test
from django.core import management
from django.core.management import CommandError
from model_bakery import baker

from devilry.apps.core.models import Subject
from devilry.devilry_account.models import PermissionGroup, SubjectPermissionGroup


class TestSubjectaddCommand(test.TestCase):
    def __run_management_command(self, subject_short_name, subject_long_name, *args):
        management.call_command(
            'devilry_subjectadd',
            subject_short_name,
            '--long-name={}'.format(subject_long_name),
            *args)

    def test_subject_with_short_name_exists_error_message(self):
        baker.make('core.Subject', short_name='test')
        with self.assertRaisesMessage(CommandError,
                                      'Subject "test" already exists.'):
            self.__run_management_command('test', 'Test')

    def test_permission_group_does_not_exist_error_message(self):
        with self.assertRaisesMessage(CommandError, 'PermissionGroup "Test group" does not exist.'):
            self.__run_management_command('test', 'Test', '--permission-groups', 'Test group')

    def test_permission_group_does_not_exist_error_subject_not_added(self):
        with self.assertRaisesMessage(CommandError, 'PermissionGroup "Test group" does not exist.'):
            self.__run_management_command('test', 'Test', '--permission-groups', 'Test group')
        self.assertEqual(Subject.objects.count(), 0)

    def test_add_subject(self):
        self.__run_management_command('test', 'Test')
        self.assertTrue(Subject.objects.filter(short_name='test').exists())

    def test_add_subject_with_permissiongroup_type_subject(self):
        baker.make('devilry_account.PermissionGroup',
                   name='Test group', grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        self.__run_management_command('test', 'Test', '--permission-groups', 'Test group')
        self.assertTrue(
            SubjectPermissionGroup.objects.filter(
                subject__short_name='test', permissiongroup__name='Test group').exists())

    def test_add_subject_with_permissiongroup_type_department(self):
        baker.make('devilry_account.PermissionGroup',
                   name='Test group', grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
        self.__run_management_command('test', 'Test', '--permission-groups', 'Test group')
        self.assertTrue(
            SubjectPermissionGroup.objects.filter(
                subject__short_name='test', permissiongroup__name='Test group').exists())

    def test_add_subject_with_multiple_permission_groups(self):
        baker.make('devilry_account.PermissionGroup',
                   name='Department admins', grouptype=PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
        baker.make('devilry_account.PermissionGroup',
                   name='Subject admins', grouptype=PermissionGroup.GROUPTYPE_SUBJECTADMIN)
        self.__run_management_command('test', 'Test', '--permission-groups', 'Department admins', 'Subject admins')
        self.assertTrue(
            SubjectPermissionGroup.objects.filter(
                subject__short_name='test', permissiongroup__name='Department admins').exists())
        self.assertTrue(
            SubjectPermissionGroup.objects.filter(
                subject__short_name='test', permissiongroup__name='Subject admins').exists())
