from django.contrib.contenttypes.models import ContentType

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_import_v2database.models import ImportedModel
from django import test
from django.conf import settings
from django.utils.dateparse import parse_datetime

from model_mommy import mommy

from devilry.apps.core.models import Candidate, RelatedStudent
from devilry.devilry_import_v2database.modelimporters.candidate_examiner_importer import CandidateImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


class TestCandidateImporter(ImporterTestCaseMixin, test.TestCase):
    def setUp(self):
        super(TestCandidateImporter, self).setUp()
        AssignmentGroupDbCacheCustomSql().initialize()

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
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.candidate',
                           data=self._create_candidate_dict(assignment_group=test_group, user=test_user))
        candidate_importer = CandidateImporter(input_root=self.temp_root_dir)
        candidate_importer.import_models()
        self.assertEquals(Candidate.objects.count(), 1)
        self.assertEquals(RelatedStudent.objects.count(), 1)

    def test_importer_pk(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.candidate',
                           data=self._create_candidate_dict(assignment_group=test_group, user=test_user))
        candidate_importer = CandidateImporter(input_root=self.temp_root_dir)
        candidate_importer.import_models()
        candidate = Candidate.objects.first()
        self.assertEquals(candidate.pk, 156)
        self.assertEquals(candidate.id, 156)

    def test_importer_assignment_group(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.candidate',
                           data=self._create_candidate_dict(assignment_group=test_group, user=test_user))
        candidate_importer = CandidateImporter(input_root=self.temp_root_dir)
        candidate_importer.import_models()
        candidate = Candidate.objects.first()
        self.assertEquals(candidate.assignment_group, test_group)

    def test_importer_related_student_user(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.candidate',
                           data=self._create_candidate_dict(assignment_group=test_group, user=test_user))
        candidate_importer = CandidateImporter(input_root=self.temp_root_dir)
        candidate_importer.import_models()
        candidate = Candidate.objects.first()
        self.assertEquals(candidate.relatedstudent.user, test_user)

    def test_importer_related_student_period(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        self.create_v2dump(model_name='core.candidate',
                           data=self._create_candidate_dict(assignment_group=test_group, user=test_user))
        candidate_importer = CandidateImporter(input_root=self.temp_root_dir)
        candidate_importer.import_models()
        candidate = Candidate.objects.first()
        self.assertEquals(candidate.relatedstudent.period, test_group.parentnode.parentnode)

    def test_importer_imported_model_created(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_group = mommy.make('core.AssignmentGroup')
        candidate_data_dict = self._create_candidate_dict(assignment_group=test_group, user=test_user)
        self.create_v2dump(model_name='core.candidate',
                           data=candidate_data_dict)
        candidate_importer = CandidateImporter(input_root=self.temp_root_dir)
        candidate_importer.import_models()
        candidate = Candidate.objects.first()
        self.assertEquals(ImportedModel.objects.count(), 1)
        imported_model = ImportedModel.objects.get(
            content_object_id=candidate.id,
            content_type=ContentType.objects.get_for_model(model=candidate)
        )
        self.assertEquals(imported_model.content_object, candidate)
        self.assertEquals(imported_model.data, candidate_data_dict)
