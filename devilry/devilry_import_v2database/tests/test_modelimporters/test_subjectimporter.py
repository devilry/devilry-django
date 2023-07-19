import unittest

from django.contrib.contenttypes.models import ContentType

from devilry.devilry_account.models import PermissionGroup, SubjectPermissionGroup
from devilry.devilry_import_v2database.models import ImportedModel
from django import test
from django.conf import settings

from model_bakery import baker

from devilry.apps.core.models import Subject
from devilry.devilry_account import models as account_models
from devilry.devilry_import_v2database.modelimporters.subject_importer import SubjectImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


@unittest.skip('Not relevant anymore, keep for history.')
class TestSubjectImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_model_meta(self):
        return {
            'model_class_name': 'Subject',
            'max_id': 16,
            'app_label': 'core'
        }

    def _create_subject_dict(self, test_admin_user=None):
        return {
            'pk': 1,
            'model': 'core.subject',
            'admin_user_ids': [test_admin_user.id] if test_admin_user else [],
            'fields': {
                'long_name': 'DUCK1010 - Programming for the natural sciences',
                'admins': [test_admin_user.id] if test_admin_user else [],
                'etag': '2017-05-15T11:04:46.567',
                'short_name': 'duck1100',
                'parentnode': 1
            }
        }

    def test_importer(self):
        test_admin_user = baker.make(settings.AUTH_USER_MODEL)
        self.create_v2dump(model_name='core.subject',
                           data=self._create_subject_dict(test_admin_user=test_admin_user))
        subjectimporter = SubjectImporter(input_root=self.temp_root_dir)
        subjectimporter.import_models()
        self.assertEqual(Subject.objects.count(), 1)

    def test_importer_pk(self):
        test_admin_user = baker.make(settings.AUTH_USER_MODEL)
        self.create_v2dump(model_name='core.subject',
                           data=self._create_subject_dict(test_admin_user=test_admin_user))
        subjectimporter = SubjectImporter(input_root=self.temp_root_dir)
        subjectimporter.import_models()
        subject = Subject.objects.first()
        self.assertEqual(subject.pk, 1)

    def test_importer_imported_model_with_admins(self):
        test_admin_user = baker.make(settings.AUTH_USER_MODEL)
        self.create_v2dump(model_name='core.subject',
                           data=self._create_subject_dict(test_admin_user=test_admin_user))
        subjectimporter = SubjectImporter(input_root=self.temp_root_dir)
        subjectimporter.import_models()
        self.assertEqual(SubjectPermissionGroup.objects.count(), 1)

    def test_importer_imported_model_without_admins(self):
        self.create_v2dump(model_name='core.subject',
                           data=self._create_subject_dict())
        subjectimporter = SubjectImporter(input_root=self.temp_root_dir)
        subjectimporter.import_models()
        self.assertEqual(SubjectPermissionGroup.objects.count(), 0)

    def test_importer_short_name(self):
        test_admin_user = baker.make(settings.AUTH_USER_MODEL)
        self.create_v2dump(model_name='core.subject',
                           data=self._create_subject_dict(test_admin_user=test_admin_user))
        subjectimporter = SubjectImporter(input_root=self.temp_root_dir)
        subjectimporter.import_models()
        subject = Subject.objects.first()
        self.assertEqual(subject.short_name, 'duck1100')

    def test_importer_long_name(self):
        test_admin_user = baker.make(settings.AUTH_USER_MODEL)
        self.create_v2dump(model_name='core.subject',
                           data=self._create_subject_dict(test_admin_user=test_admin_user))
        subjectimporter = SubjectImporter(input_root=self.temp_root_dir)
        subjectimporter.import_models()
        subject = Subject.objects.first()
        self.assertEqual(subject.long_name, 'DUCK1010 - Programming for the natural sciences')

    def test_importer_permissiongroups_is_created(self):
        test_admin_user = baker.make(settings.AUTH_USER_MODEL)
        self.create_v2dump(model_name='core.subject',
                           data=self._create_subject_dict(test_admin_user=test_admin_user))
        subjectimporter = SubjectImporter(input_root=self.temp_root_dir)
        subjectimporter.import_models()
        self.assertEqual(Subject.objects.count(), 1)
        subject = Subject.objects.first()
        self.assertEqual(account_models.PermissionGroup.objects.count(), 1)
        self.assertEqual(account_models.SubjectPermissionGroup.objects.count(), 1)
        subjects_for_admin_list = Subject.objects.filter_user_is_admin(test_admin_user)
        self.assertEqual(len(subjects_for_admin_list), 1)
        self.assertEqual(subjects_for_admin_list[0], subject)

    def test_auto_sequence_numbered_objects_uses_meta_max_id(self):
        test_admin_user = baker.make(settings.AUTH_USER_MODEL)
        self.create_v2dump(model_name='core.subject',
                           data=self._create_subject_dict(test_admin_user=test_admin_user),
                           model_meta=self._create_model_meta())
        subjectimporter = SubjectImporter(input_root=self.temp_root_dir)
        subjectimporter.import_models()
        self.assertEqual(Subject.objects.count(), 1)
        subject = Subject.objects.first()
        self.assertEqual(subject.pk, 1)
        self.assertEqual(subject.id, 1)
        subject_with_auto_id = baker.make('core.Subject')
        self.assertEqual(subject_with_auto_id.id, self._create_model_meta()['max_id']+1)
        self.assertEqual(subject_with_auto_id.pk, self._create_model_meta()['max_id']+1)
