import unittest

from django import test
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from model_bakery import baker

from devilry.apps.core.models import Period
from devilry.devilry_account import models as account_models
from devilry.devilry_account.models import SubjectPermissionGroup
from devilry.devilry_import_v2database.modelimporters.period_importer import PeriodImporter
from devilry.devilry_import_v2database.models import ImportedModel
from devilry.utils import datetimeutils
from .importer_testcase_mixin import ImporterTestCaseMixin


@unittest.skip('Not relevant anymore, keep for history.')
class TestPeriodImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_model_meta(self):
        return {
            'model_class_name': 'Period',
            'max_id': 16,
            'app_label': 'core'
        }

    def _create_period_dict(self, subject, test_admin_user=None):
        return {
            'pk': 1,
            'model': 'core.period',
            'admin_user_ids': [test_admin_user.id] if test_admin_user else [],
            'fields': {
                'short_name': 'testsemester',
                'start_time': '2017-02-14T11:04:46.585',
                'parentnode': subject.id,
                'long_name': 'Testsemester',
                'admins': [test_admin_user.id] if test_admin_user else [],
                'etag': '2017-05-15T11:04:46.585',
                'end_time': '2017-08-13T11:04:46.585'
            }
        }

    def test_import(self):
        test_admin_user = baker.make(settings.AUTH_USER_MODEL)
        test_subject = baker.make('core.Subject')
        self.create_v2dump(model_name='core.period',
                           data=self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user))
        periodimporter = PeriodImporter(input_root=self.temp_root_dir)
        periodimporter.import_models()
        self.assertEqual(Period.objects.count(), 1)

    def test_importer_pk(self):
        test_admin_user = baker.make(settings.AUTH_USER_MODEL)
        test_subject = baker.make('core.Subject')
        self.create_v2dump(model_name='core.period',
                           data=self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user))
        periodimporter = PeriodImporter(input_root=self.temp_root_dir)
        periodimporter.import_models()
        period = Period.objects.first()
        self.assertEqual(period.id, 1)

    def test_importer_imported_model_with_admins(self):
        test_admin_user = baker.make(settings.AUTH_USER_MODEL)
        test_subject = baker.make('core.Subject')
        period_data_dict = self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user)
        self.create_v2dump(model_name='core.period',
                           data=period_data_dict)
        subjectimporter = PeriodImporter(input_root=self.temp_root_dir)
        subjectimporter.import_models()
        self.assertEqual(SubjectPermissionGroup.objects.count(), 1)

    def test_importer_imported_model_without_admins(self):
        test_subject = baker.make('core.Subject')
        period_data_dict = self._create_period_dict(subject=test_subject)
        self.create_v2dump(model_name='core.period',
                           data=period_data_dict)
        subjectimporter = PeriodImporter(input_root=self.temp_root_dir)
        subjectimporter.import_models()
        self.assertEqual(SubjectPermissionGroup.objects.count(), 0)

    def test_importer_short_name(self):
        test_admin_user = baker.make(settings.AUTH_USER_MODEL)
        test_subject = baker.make('core.Subject')
        self.create_v2dump(model_name='core.period',
                           data=self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user))
        periodimporter = PeriodImporter(input_root=self.temp_root_dir)
        periodimporter.import_models()
        period = Period.objects.first()
        self.assertEqual(period.short_name, 'testsemester')

    def test_importer_long_name(self):
        test_admin_user = baker.make(settings.AUTH_USER_MODEL)
        test_subject = baker.make('core.Subject')
        self.create_v2dump(model_name='core.period',
                           data=self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user))
        periodimporter = PeriodImporter(input_root=self.temp_root_dir)
        periodimporter.import_models()
        period = Period.objects.first()
        self.assertEqual(period.long_name, 'Testsemester')

    def test_importer_start_time(self):
        test_admin_user = baker.make(settings.AUTH_USER_MODEL)
        test_subject = baker.make('core.Subject')
        self.create_v2dump(model_name='core.period',
                           data=self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user))
        periodimporter = PeriodImporter(input_root=self.temp_root_dir)
        periodimporter.import_models()
        period = Period.objects.first()
        start_time = datetimeutils.from_isoformat('2017-02-14T11:04:46.585')
        self.assertEqual(period.start_time, start_time)

    def test_importer_end_time(self):
        test_admin_user = baker.make(settings.AUTH_USER_MODEL)
        test_subject = baker.make('core.Subject')
        self.create_v2dump(model_name='core.period',
                           data=self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user))
        periodimporter = PeriodImporter(input_root=self.temp_root_dir)
        periodimporter.import_models()
        period = Period.objects.first()
        end_time = datetimeutils.from_isoformat('2017-08-13T11:04:46.585')
        self.assertEqual(period.end_time, end_time)

    def test_importer_subject(self):
        test_admin_user = baker.make(settings.AUTH_USER_MODEL)
        test_subject = baker.make('core.Subject')
        self.create_v2dump(model_name='core.period',
                           data=self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user))
        periodimporter = PeriodImporter(input_root=self.temp_root_dir)
        periodimporter.import_models()
        period = Period.objects.first()
        self.assertEqual(period.parentnode, test_subject)

    def test_importer_permissiongroup_is_created(self):
        test_admin_user = baker.make(settings.AUTH_USER_MODEL)
        test_subject = baker.make('core.Subject')
        self.create_v2dump(model_name='core.period',
                           data=self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user))
        periodimporter = PeriodImporter(input_root=self.temp_root_dir)
        periodimporter.import_models()
        self.assertEqual(Period.objects.count(), 1)
        period = Period.objects.first()
        self.assertEqual(account_models.PermissionGroup.objects.count(), 1)
        self.assertEqual(account_models.PermissionGroupUser.objects.count(), 1)
        self.assertEqual(account_models.SubjectPermissionGroup.objects.count(), 1)
        periods_for_admin_list = Period.objects.filter_user_is_admin(test_admin_user)
        self.assertEqual(len(periods_for_admin_list), 1)
        self.assertEqual(periods_for_admin_list[0], period)

    def test_auto_sequence_numbered_objects_uses_meta_max_id(self):
        test_admin_user = baker.make(settings.AUTH_USER_MODEL)
        test_subject = baker.make('core.Subject')
        self.create_v2dump(model_name='core.period',
                           data=self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user),
                           model_meta=self._create_model_meta())
        periodimporter = PeriodImporter(input_root=self.temp_root_dir)
        periodimporter.import_models()
        self.assertEqual(Period.objects.count(), 1)
        period = Period.objects.first()
        self.assertEqual(period.pk, 1)
        self.assertEqual(period.id, 1)
        period_with_auto_id = baker.make('core.Period')
        self.assertEqual(period_with_auto_id.id, self._create_model_meta()['max_id']+1)
        self.assertEqual(period_with_auto_id.pk, self._create_model_meta()['max_id']+1)
