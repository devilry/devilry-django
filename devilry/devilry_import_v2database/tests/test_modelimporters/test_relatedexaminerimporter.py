from django.contrib.contenttypes.models import ContentType

from devilry.devilry_import_v2database.models import ImportedModel
from django import test
from django.conf import settings
from django.utils.dateparse import parse_datetime

from model_mommy import mommy

from devilry.apps.core.models import RelatedExaminer, PeriodTag, Period
from devilry.devilry_import_v2database.modelimporters.relateduser_importer import RelatedExaminerImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


class TestRelatedExaminerImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_model_meta(self):
        return {
            'model_class_name': 'RelatedExaminer',
            'max_id': 16,
            'app_label': 'core'
        }

    def _create_related_examiner_dict(self, period, user):
        return {
            'pk': 6,
            'model': 'core.relatedexaminer',
            'fields': {
                'user': user.id,
                'period': period.id,
                'tags': 'group2'
            }
        }

    def test_importer(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        self.create_v2dump(model_name='core.relatedexaminer',
                           data=self._create_related_examiner_dict(period=test_period, user=test_user))
        relatedexaminer_importer = RelatedExaminerImporter(input_root=self.temp_root_dir)
        relatedexaminer_importer.import_models()
        self.assertEquals(RelatedExaminer.objects.count(), 1)
        self.assertEquals(PeriodTag.objects.count(), 1)

    def test_importer_related_examiner_pk(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        self.create_v2dump(model_name='core.relatedexaminer',
                           data=self._create_related_examiner_dict(period=test_period, user=test_user))
        relatedexaminer_importer = RelatedExaminerImporter(input_root=self.temp_root_dir)
        relatedexaminer_importer.import_models()
        related_examiner = RelatedExaminer.objects.first()
        self.assertEquals(related_examiner.pk, 6)
        self.assertEquals(related_examiner.id, 6)

    # def test_importer_period_tag_period(self):
    #     test_user = mommy.make(settings.AUTH_USER_MODEL)
    #     test_period = mommy.make('core.Period')
    #     self.create_v2dump(model_name='core.relatedexaminer',
    #                        data=self._create_related_examiner_dict(period=test_period, user=test_user))
    #     relatedexaminer_importer = RelatedExaminerImporter(input_root=self.temp_root_dir)
    #     relatedexaminer_importer.import_models()
    #     period_tag = PeriodTag.objects.first()
    #     self.assertEquals(period_tag.period, test_period)
    #     self.assertEquals(ImportedModel.objects.count(), 1)

    def test_importer_period_tag_single_tag_created(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        self.create_v2dump(model_name='core.relatedexaminer',
                           data=self._create_related_examiner_dict(period=test_period, user=test_user))
        relatedexaminer_importer = RelatedExaminerImporter(input_root=self.temp_root_dir)
        relatedexaminer_importer.import_models()
        period_tag = PeriodTag.objects.first()
        self.assertEquals(period_tag.tag, 'group2')

    def test_importer_period_tag_multiple_tags_created(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        relatedexaminer_data_dict = self._create_related_examiner_dict(period=test_period, user=test_user)
        relatedexaminer_data_dict['fields']['tags'] = 'group1,group2'
        self.create_v2dump(model_name='core.relatedexaminer',
                           data=relatedexaminer_data_dict)
        relatedexaminer_importer = RelatedExaminerImporter(input_root=self.temp_root_dir)
        relatedexaminer_importer.import_models()
        period_tags_list = [period_tag.tag for period_tag in PeriodTag.objects.all()]
        self.assertEquals(len(period_tags_list), 2)
        self.assertIn('group1', period_tags_list)
        self.assertIn('group2', period_tags_list)

    def test_importer_single_period_tag_examiner_is_added(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        self.create_v2dump(model_name='core.relatedexaminer',
                           data=self._create_related_examiner_dict(period=test_period, user=test_user))
        relatedexaminer_importer = RelatedExaminerImporter(input_root=self.temp_root_dir)
        relatedexaminer_importer.import_models()
        related_examiner = RelatedExaminer.objects.first()
        period_tag = PeriodTag.objects.first()
        self.assertEquals(period_tag.relatedexaminers.count(), 1)
        self.assertIn(related_examiner, period_tag.relatedexaminers.all())

    def test_importer_multiple_period_tags_examiner_is_added(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        relatedexaminer_data_dict = self._create_related_examiner_dict(period=test_period, user=test_user)
        relatedexaminer_data_dict['fields']['tags'] = 'group1,group2'
        self.create_v2dump(model_name='core.relatedexaminer',
                           data=relatedexaminer_data_dict)
        relatedexaminer_importer = RelatedExaminerImporter(input_root=self.temp_root_dir)
        relatedexaminer_importer.import_models()
        related_examiner = RelatedExaminer.objects.first()
        period_tags = PeriodTag.objects.all()
        self.assertEquals(period_tags.count(), 2)
        for period_tag in period_tags:
            self.assertIn(related_examiner, period_tag.relatedexaminers.all())

    def test_importer_examiner_is_added_to_existing_tags_and_new_tags(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=test_period, tag='group1')
        mommy.make('core.PeriodTag', period=test_period, tag='group3')
        relatedexaminer_data_dict = self._create_related_examiner_dict(period=test_period, user=test_user)
        relatedexaminer_data_dict['fields']['tags'] = 'group1,group2,group3,group4'
        self.create_v2dump(model_name='core.relatedexaminer',
                           data=relatedexaminer_data_dict)
        relatedexaminer_importer = RelatedExaminerImporter(input_root=self.temp_root_dir)
        relatedexaminer_importer.import_models()
        related_examiner = RelatedExaminer.objects.first()
        period_tags = PeriodTag.objects.all()
        self.assertEquals(period_tags.count(), 4)
        for period_tag in period_tags:
            self.assertIn(related_examiner, period_tag.relatedexaminers.all())

    # def test_importer_imported_model_created(self):
    #     test_user = mommy.make(settings.AUTH_USER_MODEL)
    #     test_period = mommy.make('core.Period')
    #     related_examiner_data_dict = self._create_related_examiner_dict(period=test_period, user=test_user)
    #     self.create_v2dump(model_name='core.relatedexaminer',
    #                        data=related_examiner_data_dict)
    #     relatedexaminer_importer = RelatedExaminerImporter(input_root=self.temp_root_dir)
    #     relatedexaminer_importer.import_models()
    #     related_examiner = RelatedExaminer.objects.first()
    #     self.assertEquals(ImportedModel.objects.count(), 1)
    #     imported_model = ImportedModel.objects.get(
    #         content_object_id=related_examiner.id,
    #         content_type=ContentType.objects.get_for_model(model=related_examiner)
    #     )
    #     self.assertEquals(imported_model.content_object, related_examiner)
    #     self.assertEquals(imported_model.data, related_examiner_data_dict)

    def test_auto_sequence_numbered_objects_uses_meta_max_id(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make('core.Period')
        self.create_v2dump(model_name='core.relatedexaminer',
                           data=self._create_related_examiner_dict(period=test_period, user=test_user),
                           model_meta=self._create_model_meta())
        relatedexaminer_importer = RelatedExaminerImporter(input_root=self.temp_root_dir)
        relatedexaminer_importer.import_models()
        self.assertEquals(RelatedExaminer.objects.count(), 1)
        related_examiner = RelatedExaminer.objects.first()
        self.assertEquals(related_examiner.pk, 6)
        self.assertEquals(related_examiner.id, 6)
        related_examiner_with_auto_id = mommy.make('core.RelatedExaminer')
        self.assertEquals(related_examiner_with_auto_id.pk, self._create_model_meta()['max_id']+1)
        self.assertEquals(related_examiner_with_auto_id.id, self._create_model_meta()['max_id']+1)
