import unittest

from devilry.devilry_account.models import PermissionGroup, SubjectPermissionGroup
from devilry.devilry_import_v2database.models import ImportedModel
from django import test
from django.conf import settings

from model_bakery import baker

from devilry.apps.core.models import Subject
from devilry.devilry_account import models as account_models
from devilry.devilry_import_v2database.modelimporters.node_importer import NodeImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


@unittest.skip('Not relevant anymore, keep for history.')
class TestNodeImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_node_dict(self, test_subject_ids=None, test_admin_user_ids=None):
        return {
            'subject_ids': test_subject_ids if test_subject_ids else [],
            'pk': 1,
            'model': 'core.node',
            'admin_user_ids': test_admin_user_ids if test_admin_user_ids else [],
            'fields': {
                'long_name': 'University of Duckburgh',
                'admins': test_admin_user_ids if test_admin_user_ids else [],
                'short_name': 'duckburgh',
                'parentnode': None
            }
        }

    def test_import(self):
        test_subject = baker.make('core.Subject')
        test_admin = baker.make(settings.AUTH_USER_MODEL)
        data_dict = self._create_node_dict(test_subject_ids=[test_subject.id], test_admin_user_ids=[test_admin.id])
        self.create_v2dump(model_name='core.node', data=data_dict)
        nodeimporter = NodeImporter(input_root=self.temp_root_dir)
        nodeimporter.import_models()
        self.assertEqual(account_models.PermissionGroup.objects.count(), 1)
        self.assertEqual(account_models.PermissionGroup.objects.first().grouptype,
                          account_models.PermissionGroup.GROUPTYPE_DEPARTMENTADMIN)
        self.assertEqual(account_models.SubjectPermissionGroup.objects.count(), 1)
        self.assertEqual(account_models.PermissionGroupUser.objects.count(), 1)

    def test_import_multiple_subjects_single_admin(self):
        test_subject1 = baker.make('core.Subject')
        test_subject2 = baker.make('core.Subject')
        test_subject3 = baker.make('core.Subject')
        subject_id_list = [test_subject1.id, test_subject2.id, test_subject3.id]
        test_admin = baker.make(settings.AUTH_USER_MODEL)
        data_dict = self._create_node_dict(test_subject_ids=subject_id_list, test_admin_user_ids=[test_admin.id])
        self.create_v2dump(model_name='core.node', data=data_dict)
        nodeimporter = NodeImporter(input_root=self.temp_root_dir)
        nodeimporter.import_models()
        self.assertEqual(account_models.PermissionGroup.objects.count(), 1)
        self.assertEqual(account_models.SubjectPermissionGroup.objects.count(), 3)

    def test_import_subject_permission_group_for_permission_group(self):
        test_subject = baker.make('core.Subject')
        test_admin = baker.make(settings.AUTH_USER_MODEL)
        data_dict = self._create_node_dict(test_subject_ids=[test_subject.id], test_admin_user_ids=[test_admin.id])
        self.create_v2dump(model_name='core.node', data=data_dict)
        nodeimporter = NodeImporter(input_root=self.temp_root_dir)
        nodeimporter.import_models()
        self.assertEqual(account_models.PermissionGroup.objects.count(), 1)
        permission_group = account_models.PermissionGroup.objects.first()
        subject_permission_group = account_models.SubjectPermissionGroup.objects.first()
        self.assertEqual(subject_permission_group.permissiongroup, permission_group)
        self.assertEqual(subject_permission_group.subject, test_subject)

    def test_import_multiple_subject_permission_groups_for_permission_group(self):
        test_subject1 = baker.make('core.Subject')
        test_subject2 = baker.make('core.Subject')
        test_subject3 = baker.make('core.Subject')
        subject_id_list = [test_subject1.id, test_subject2.id, test_subject3.id]
        test_admin = baker.make(settings.AUTH_USER_MODEL)
        data_dict = self._create_node_dict(test_subject_ids=subject_id_list, test_admin_user_ids=[test_admin.id])
        self.create_v2dump(model_name='core.node', data=data_dict)
        nodeimporter = NodeImporter(input_root=self.temp_root_dir)
        nodeimporter.import_models()
        self.assertEqual(account_models.PermissionGroup.objects.count(), 1)
        permission_group = account_models.PermissionGroup.objects.first()
        subject_permission_groups = account_models.SubjectPermissionGroup.objects.all()
        for subject_permission_group in subject_permission_groups:
            self.assertEqual(subject_permission_group.permissiongroup, permission_group)

    def test_import_permission_group_user_on_permission_group(self):
        test_subject = baker.make('core.Subject')
        test_admin = baker.make(settings.AUTH_USER_MODEL)
        data_dict = self._create_node_dict(test_subject_ids=[test_subject.id], test_admin_user_ids=[test_admin.id])
        self.create_v2dump(model_name='core.node', data=data_dict)
        nodeimporter = NodeImporter(input_root=self.temp_root_dir)
        nodeimporter.import_models()
        self.assertEqual(account_models.PermissionGroupUser.objects.count(), 1)
        permission_group = account_models.PermissionGroup.objects.first()
        permission_group_user = account_models.PermissionGroupUser.objects.first()
        self.assertEqual(permission_group_user.user, test_admin)
        self.assertEqual(permission_group_user.permissiongroup, permission_group)

    def test_import_user_is_admin_for_subject(self):
        test_subject = baker.make('core.Subject')
        test_subject_no_admins = baker.make('core.Subject')
        test_admin = baker.make(settings.AUTH_USER_MODEL)
        data_dict = self._create_node_dict(test_subject_ids=[test_subject.id], test_admin_user_ids=[test_admin.id])
        self.create_v2dump(model_name='core.node', data=data_dict)
        nodeimporter = NodeImporter(input_root=self.temp_root_dir)
        nodeimporter.import_models()
        subject_queryset = Subject.objects.filter_user_is_admin(user=test_admin)
        self.assertEqual(subject_queryset.count(), 1)
        self.assertIn(test_subject, subject_queryset)
        self.assertNotIn(test_subject_no_admins, subject_queryset)

    def test_import_user_is_admin_for_multiple_subjects(self):
        test_subject1 = baker.make('core.Subject')
        test_subject2 = baker.make('core.Subject')
        test_subject3 = baker.make('core.Subject')
        test_subject_no_admins = baker.make('core.Subject')
        test_admin = baker.make(settings.AUTH_USER_MODEL)
        test_subject_ids = [test_subject1.id, test_subject2.id, test_subject3.id]
        data_dict = self._create_node_dict(test_subject_ids=test_subject_ids, test_admin_user_ids=[test_admin.id])
        self.create_v2dump(model_name='core.node', data=data_dict)
        nodeimporter = NodeImporter(input_root=self.temp_root_dir)
        nodeimporter.import_models()
        subject_queryset = Subject.objects.filter_user_is_admin(user=test_admin)
        self.assertEqual(subject_queryset.count(), 3)
        self.assertIn(test_subject1, subject_queryset)
        self.assertIn(test_subject2, subject_queryset)
        self.assertIn(test_subject3, subject_queryset)
        self.assertNotIn(test_subject_no_admins, subject_queryset)
