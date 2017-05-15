from devilry.devilry_import_v2database.models import ImportedModel
from django import test
from django.conf import settings

from model_mommy import mommy

from devilry.apps.core.models import Subject
from devilry.devilry_account import models as account_models
from devilry.devilry_import_v2database.modelimporters.subjectimporter import SubjectImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


class TestSubjectImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_subject_dict(self, test_admin_user):
        return {
            'pk': 1,
            'model': 'core.subject',
            'admin_user_ids': [test_admin_user.id],
            'fields': {
                'long_name': 'DUCK1010 - Programming for the natural sciences',
                'admins': [test_admin_user.id],
                'etag': '2017-05-15T11:04:46.567',
                'short_name': 'duck1100',
                'parentnode': 1
            }
        }

    def test_importer(self):
        test_admin_user = mommy.make(settings.AUTH_USER_MODEL)
        self.create_v2dump(model_name='core.subject',
                           data=self._create_subject_dict(test_admin_user=test_admin_user))
        subjectimporter = SubjectImporter(input_root=self.temp_root_dir)
        subjectimporter.import_models()
        self.assertEquals(Subject.objects.count(), 1)

    def test_importer_pk(self):
        test_admin_user = mommy.make(settings.AUTH_USER_MODEL)
        self.create_v2dump(model_name='core.subject',
                           data=self._create_subject_dict(test_admin_user=test_admin_user))
        subjectimporter = SubjectImporter(input_root=self.temp_root_dir)
        subjectimporter.import_models()
        subject = Subject.objects.first()
        self.assertEquals(subject.pk, 1)

    def test_importer_short_name(self):
        test_admin_user = mommy.make(settings.AUTH_USER_MODEL)
        self.create_v2dump(model_name='core.subject',
                           data=self._create_subject_dict(test_admin_user=test_admin_user))
        subjectimporter = SubjectImporter(input_root=self.temp_root_dir)
        subjectimporter.import_models()
        subject = Subject.objects.first()
        self.assertEquals(subject.short_name, 'duck1100')

    def test_importer_long_name(self):
        test_admin_user = mommy.make(settings.AUTH_USER_MODEL)
        self.create_v2dump(model_name='core.subject',
                           data=self._create_subject_dict(test_admin_user=test_admin_user))
        subjectimporter = SubjectImporter(input_root=self.temp_root_dir)
        subjectimporter.import_models()
        subject = Subject.objects.first()
        self.assertEquals(subject.long_name, 'DUCK1010 - Programming for the natural sciences')

    def test_importer_permissiongroups_is_created(self):
        test_admin_user = mommy.make(settings.AUTH_USER_MODEL)
        self.create_v2dump(model_name='core.subject',
                           data=self._create_subject_dict(test_admin_user=test_admin_user))
        subjectimporter = SubjectImporter(input_root=self.temp_root_dir)
        subjectimporter.import_models()
        self.assertEquals(Subject.objects.count(), 1)
        subject = Subject.objects.first()
        self.assertEquals(account_models.PermissionGroup.objects.count(), 1)
        self.assertEquals(account_models.SubjectPermissionGroup.objects.count(), 1)
        subjects_for_admin_list = Subject.objects.filter_user_is_admin(test_admin_user)
        self.assertEquals(len(subjects_for_admin_list), 1)
        self.assertEquals(subjects_for_admin_list[0], subject)

    def test_importer_imported_model_created(self):
        test_admin_user = mommy.make(settings.AUTH_USER_MODEL)
        subject_data_dict = self._create_subject_dict(test_admin_user=test_admin_user)
        self.create_v2dump(model_name='core.subject',
                           data=subject_data_dict)
        subjectimporter = SubjectImporter(input_root=self.temp_root_dir)
        subjectimporter.import_models()
        self.assertEquals(ImportedModel.objects.count(), 1)
        imported_model = ImportedModel.objects.first()
        self.assertEquals(imported_model.data, subject_data_dict)
