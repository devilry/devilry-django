import unittest

from django.contrib.contenttypes.models import ContentType

from devilry.devilry_import_v2database.models import ImportedModel
from django import test
from django.conf import settings

from model_bakery import baker

from devilry.apps.core.models import Examiner, RelatedExaminer
from devilry.devilry_import_v2database.modelimporters.candidate_examiner_importer import ExaminerImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


@unittest.skip('Not relevant anymore, keep for history.')
class TestExaminerImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_model_meta(self):
        return {
            'model_class_name': 'Examiner',
            'max_id': 156,
            'app_label': 'core'
        }

    def _create_examiner_dict(self, assignment_group, user):
        return {
            'pk': 156,
            'model': 'core.examiner',
            'fields': {
                'user': user.id,
                'assignmentgroup': assignment_group.id}
        }

    def test_importer(self):
        test_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.examiner',
                           data=self._create_examiner_dict(assignment_group=test_group, user=test_user))
        examiner_importer = ExaminerImporter(input_root=self.temp_root_dir)
        examiner_importer.import_models()
        self.assertEqual(Examiner.objects.count(), 1)
        self.assertEqual(RelatedExaminer.objects.count(), 1)

    def test_importer_pk(self):
        test_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.examiner',
                           data=self._create_examiner_dict(assignment_group=test_group, user=test_user))
        examiner_importer = ExaminerImporter(input_root=self.temp_root_dir)
        examiner_importer.import_models()
        examiner = Examiner.objects.first()
        self.assertEqual(examiner.pk, 156)
        self.assertEqual(examiner.id, 156)

    def test_importer_assignment_group(self):
        test_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.examiner',
                           data=self._create_examiner_dict(assignment_group=test_group, user=test_user))
        examiner_importer = ExaminerImporter(input_root=self.temp_root_dir)
        examiner_importer.import_models()
        examiner = Examiner.objects.first()
        self.assertEqual(examiner.assignmentgroup, test_group)

    def test_importer_existing_related_examiner_active_is_true(self):
        test_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        baker.make('core.RelatedExaminer', period=test_group.parentnode.parentnode, user=test_user)
        self.create_v2dump(model_name='core.examiner',
                           data=self._create_examiner_dict(assignment_group=test_group, user=test_user))
        examiner_importer = ExaminerImporter(input_root=self.temp_root_dir)
        examiner_importer.import_models()
        self.assertEqual(RelatedExaminer.objects.count(), 1)
        related_examiner = RelatedExaminer.objects.first()
        self.assertTrue(related_examiner.active)

    def test_importer_related_examiner_with_active_false_is_created(self):
        test_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.examiner',
                           data=self._create_examiner_dict(assignment_group=test_group, user=test_user))
        examiner_importer = ExaminerImporter(input_root=self.temp_root_dir)
        examiner_importer.import_models()
        self.assertEqual(RelatedExaminer.objects.count(), 1)
        related_examiner = RelatedExaminer.objects.first()
        self.assertFalse(related_examiner.active)

    def test_importer_related_examiner_user(self):
        test_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.examiner',
                           data=self._create_examiner_dict(assignment_group=test_group, user=test_user))
        examiner_importer = ExaminerImporter(input_root=self.temp_root_dir)
        examiner_importer.import_models()
        examiner = Examiner.objects.first()
        self.assertEqual(examiner.relatedexaminer.user, test_user)

    def test_importer_related_examiner_period(self):
        test_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.examiner',
                           data=self._create_examiner_dict(assignment_group=test_group, user=test_user))
        examiner_importer = ExaminerImporter(input_root=self.temp_root_dir)
        examiner_importer.import_models()
        examiner = Examiner.objects.first()
        self.assertEqual(examiner.relatedexaminer.period, test_group.parentnode.parentnode)

    def test_auto_sequence_numbered_objects_uses_meta_max_id(self):
        test_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.examiner',
                           data=self._create_examiner_dict(assignment_group=test_group, user=test_user),
                           model_meta=self._create_model_meta())
        examiner_importer = ExaminerImporter(input_root=self.temp_root_dir)
        examiner_importer.import_models()
        self.assertEqual(Examiner.objects.count(), 1)
        examiner = Examiner.objects.first()
        self.assertEqual(examiner.pk, 156)
        self.assertEqual(examiner.id, 156)
        examiner_with_auto_id = baker.make('core.Examiner')
        self.assertEqual(examiner_with_auto_id.pk, self._create_model_meta()['max_id']+1)
        self.assertEqual(examiner_with_auto_id.id, self._create_model_meta()['max_id']+1)
