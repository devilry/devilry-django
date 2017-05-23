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

    def test_importer_single_period_tag_examiner_is_added(self):
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

    def test_importer_multiple_period_tags_examiner_is_added(self):
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

    def test_importer_examiner_is_added_to_existing_tags_and_new_tags(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=test_period, tag='group1')
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
