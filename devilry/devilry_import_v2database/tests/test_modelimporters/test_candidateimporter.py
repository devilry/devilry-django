import unittest

from django.contrib.contenttypes.models import ContentType

from devilry.devilry_import_v2database.models import ImportedModel
from django import test
from django.conf import settings
from django.utils.dateparse import parse_datetime

from model_bakery import baker

from devilry.apps.core.models import Candidate, RelatedStudent
from devilry.devilry_import_v2database.modelimporters.candidate_examiner_importer import CandidateImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


@unittest.skip('Not relevant anymore, keep for history.')
class TestCandidateImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_model_meta(self):
        return {
            'model_class_name': 'Candidate',
            'max_id': 156,
            'app_label': 'core'
        }

    def _create_candidate_dict(self, assignment_group, user):
        return {
            'pk': 156,
            'model': 'core.candidate',
            'fields': {
                'candidate_id': None,
                'student': user.id,
                'assignment_group': assignment_group.id
            }
        }

    def test_importer(self):
        test_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.candidate',
                           data=self._create_candidate_dict(assignment_group=test_group, user=test_user))
        candidate_importer = CandidateImporter(input_root=self.temp_root_dir)
        candidate_importer.import_models()
        self.assertEqual(Candidate.objects.count(), 1)
        self.assertEqual(RelatedStudent.objects.count(), 1)

    def test_importer_pk(self):
        test_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.candidate',
                           data=self._create_candidate_dict(assignment_group=test_group, user=test_user))
        candidate_importer = CandidateImporter(input_root=self.temp_root_dir)
        candidate_importer.import_models()
        candidate = Candidate.objects.first()
        self.assertEqual(candidate.pk, 156)
        self.assertEqual(candidate.id, 156)

    def test_importer_assignment_group(self):
        test_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.candidate',
                           data=self._create_candidate_dict(assignment_group=test_group, user=test_user))
        candidate_importer = CandidateImporter(input_root=self.temp_root_dir)
        candidate_importer.import_models()
        candidate = Candidate.objects.first()
        self.assertEqual(candidate.assignment_group, test_group)

    def test_importer_existing_related_candidate_active_is_true(self):
        test_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        baker.make('core.RelatedStudent', period=test_group.parentnode.parentnode, user=test_user)
        self.create_v2dump(model_name='core.candidate',
                           data=self._create_candidate_dict(assignment_group=test_group, user=test_user))
        candidate_importer = CandidateImporter(input_root=self.temp_root_dir)
        candidate_importer.import_models()
        self.assertEqual(RelatedStudent.objects.count(), 1)
        related_candidate = RelatedStudent.objects.first()
        self.assertTrue(related_candidate.active)

    def test_importer_related_candidate_with_active_false_is_created(self):
        test_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.candidate',
                           data=self._create_candidate_dict(assignment_group=test_group, user=test_user))
        candidate_importer = CandidateImporter(input_root=self.temp_root_dir)
        candidate_importer.import_models()
        self.assertEqual(RelatedStudent.objects.count(), 1)
        related_student = RelatedStudent.objects.first()
        self.assertFalse(related_student.active)

    def test_importer_related_candidate_user(self):
        test_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.candidate',
                           data=self._create_candidate_dict(assignment_group=test_group, user=test_user))
        candidate_importer = CandidateImporter(input_root=self.temp_root_dir)
        candidate_importer.import_models()
        candidate = Candidate.objects.first()
        self.assertEqual(candidate.relatedstudent.user, test_user)

    def test_importer_related_candidate_period(self):
        test_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.candidate',
                           data=self._create_candidate_dict(assignment_group=test_group, user=test_user))
        candidate_importer = CandidateImporter(input_root=self.temp_root_dir)
        candidate_importer.import_models()
        candidate = Candidate.objects.first()
        self.assertEqual(candidate.relatedstudent.period, test_group.parentnode.parentnode)

    def test_auto_sequence_numbered_objects_uses_meta_max_id(self):
        test_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.candidate',
                           data=self._create_candidate_dict(assignment_group=test_group, user=test_user),
                           model_meta=self._create_model_meta())
        candidate_importer = CandidateImporter(input_root=self.temp_root_dir)
        candidate_importer.import_models()
        self.assertEqual(Candidate.objects.count(), 1)
        candidate = Candidate.objects.first()
        self.assertEqual(candidate.pk, 156)
        self.assertEqual(candidate.id, 156)
        candidate_with_auto_id = baker.make('core.Candidate')
        self.assertEqual(candidate_with_auto_id.pk, self._create_model_meta()['max_id']+1)
        self.assertEqual(candidate_with_auto_id.id, self._create_model_meta()['max_id']+1)
