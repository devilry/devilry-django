from django.contrib.contenttypes.models import ContentType

from devilry.devilry_import_v2database.models import ImportedModel
from django import test
from django.conf import settings
from django.utils.dateparse import parse_datetime

from model_mommy import mommy

from devilry.apps.core.models import RelatedStudent, PeriodTag, Period
from devilry.devilry_import_v2database.modelimporters.relateduser_importer import RelatedStudentImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


class TestRelatedStudentImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_model_meta(self):
        return {
            'model_class_name': 'RelatedStudent',
            'max_id': 19,
            'app_label': 'core'
        }

    def _create_related_student_dict(self, period, user):
        return {
            'pk': 19,
            'model': 'core.relatedstudent',
            'fields': {
                'user': user.id,
                'period': period.id,
                'candidate_id': None,
                'tags': 'group1'
            }
        }

    def test_importer(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        self.create_v2dump(model_name='core.relatedstudent',
                           data=self._create_related_student_dict(period=test_period, user=test_user))
        relatedstudent_importer = RelatedStudentImporter(input_root=self.temp_root_dir)
        relatedstudent_importer.import_models()
        self.assertEquals(RelatedStudent.objects.count(), 1)
        self.assertEquals(PeriodTag.objects.count(), 1)

    def test_importer_related_examiner_pk(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        self.create_v2dump(model_name='core.relatedstudent',
                           data=self._create_related_student_dict(period=test_period, user=test_user))
        relatedstudent_importer = RelatedStudentImporter(input_root=self.temp_root_dir)
        relatedstudent_importer.import_models()
        related_examiner = RelatedStudent.objects.first()
        self.assertEquals(related_examiner.pk, 19)
        self.assertEquals(related_examiner.id, 19)

    def test_importer_period_tag_period(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        self.create_v2dump(model_name='core.relatedstudent',
                           data=self._create_related_student_dict(period=test_period, user=test_user))
        relatedstudent_importer = RelatedStudentImporter(input_root=self.temp_root_dir)
        relatedstudent_importer.import_models()
        period_tag = PeriodTag.objects.first()
        self.assertEquals(period_tag.period, test_period)

    def test_importer_period_tag_single_tag_created(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        self.create_v2dump(model_name='core.relatedstudent',
                           data=self._create_related_student_dict(period=test_period, user=test_user))
        relatedstudent_importer = RelatedStudentImporter(input_root=self.temp_root_dir)
        relatedstudent_importer.import_models()
        period_tag = PeriodTag.objects.first()
        self.assertEquals(period_tag.tag, 'group1')

    def test_importer_period_tag_multiple_tags_created(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        relatedexaminer_data_dict = self._create_related_student_dict(period=test_period, user=test_user)
        relatedexaminer_data_dict['fields']['tags'] = 'group1,group2'
        self.create_v2dump(model_name='core.relatedstudent',
                           data=relatedexaminer_data_dict)
        relatedstudent_importer = RelatedStudentImporter(input_root=self.temp_root_dir)
        relatedstudent_importer.import_models()
        period_tags_list = [period_tag.tag for period_tag in PeriodTag.objects.all()]
        self.assertEquals(len(period_tags_list), 2)
        self.assertIn('group1', period_tags_list)
        self.assertIn('group2', period_tags_list)

    def test_importer_single_period_tag_related_student_is_added(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        self.create_v2dump(model_name='core.relatedstudent',
                           data=self._create_related_student_dict(period=test_period, user=test_user))
        relatedstudent_importer = RelatedStudentImporter(input_root=self.temp_root_dir)
        relatedstudent_importer.import_models()
        related_examiner = RelatedStudent.objects.first()
        period_tag = PeriodTag.objects.first()
        self.assertEquals(period_tag.relatedstudents.count(), 1)
        self.assertIn(related_examiner, period_tag.relatedstudents.all())

    def test_importer_multiple_period_tags_related_student_is_added(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        relatedexaminer_data_dict = self._create_related_student_dict(period=test_period, user=test_user)
        relatedexaminer_data_dict['fields']['tags'] = 'group1,group2'
        self.create_v2dump(model_name='core.relatedstudent',
                           data=relatedexaminer_data_dict)
        relatedstudent_importer = RelatedStudentImporter(input_root=self.temp_root_dir)
        relatedstudent_importer.import_models()
        related_examiner = RelatedStudent.objects.first()
        period_tags = PeriodTag.objects.all()
        self.assertEquals(period_tags.count(), 2)
        for period_tag in period_tags:
            self.assertIn(related_examiner, period_tag.relatedstudents.all())

    def test_importer_related_student_is_added_to_existing_tags_and_new_tags(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=test_period, tag='group1')
        mommy.make('core.PeriodTag', period=test_period, tag='group4')
        relatedexaminer_data_dict = self._create_related_student_dict(period=test_period, user=test_user)
        relatedexaminer_data_dict['fields']['tags'] = 'group1,group2,group3,group4'
        self.create_v2dump(model_name='core.relatedstudent',
                           data=relatedexaminer_data_dict)
        relatedstudent_importer = RelatedStudentImporter(input_root=self.temp_root_dir)
        relatedstudent_importer.import_models()
        related_examiner = RelatedStudent.objects.first()
        period_tags = PeriodTag.objects.all()
        self.assertEquals(period_tags.count(), 4)
        for period_tag in period_tags:
            self.assertIn(related_examiner, period_tag.relatedstudents.all())

    def test_importer_imported_model_created(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        related_student_data_dict = self._create_related_student_dict(period=test_period, user=test_user)
        self.create_v2dump(model_name='core.relatedstudent',
                           data=related_student_data_dict)
        relatedstudent_importer = RelatedStudentImporter(input_root=self.temp_root_dir)
        relatedstudent_importer.import_models()
        related_student = RelatedStudent.objects.first()
        self.assertEquals(ImportedModel.objects.count(), 1)
        imported_model = ImportedModel.objects.get(
            content_object_id=related_student.id,
            content_type=ContentType.objects.get_for_model(model=related_student)
        )
        self.assertEquals(imported_model.content_object, related_student)
        self.assertEquals(imported_model.data, related_student_data_dict)

    def test_auto_sequence_numbered_objects_uses_meta_max_id(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        self.create_v2dump(model_name='core.relatedstudent',
                           data=self._create_related_student_dict(period=test_period, user=test_user),
                           model_meta=self._create_model_meta())
        relatedstudent_importer = RelatedStudentImporter(input_root=self.temp_root_dir)
        relatedstudent_importer.import_models()
        self.assertEquals(RelatedStudent.objects.count(), 1)
        related_student = RelatedStudent.objects.first()
        self.assertEquals(related_student.pk, 19)
        self.assertEquals(related_student.id, 19)
        related_student_with_auto_id = mommy.make('core.RelatedStudent')
        self.assertEquals(related_student_with_auto_id.pk, self._create_model_meta()['max_id']+1)
        self.assertEquals(related_student_with_auto_id.id, self._create_model_meta()['max_id']+1)
