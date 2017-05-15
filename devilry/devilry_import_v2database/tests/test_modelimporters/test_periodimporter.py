from django import test
from django.conf import settings
from django.utils.dateparse import parse_datetime

from model_mommy import mommy

from devilry.apps.core.models import Period
from devilry.devilry_account import models as account_models
from devilry.devilry_import_v2database.modelimporters.periodimporter import PeriodImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


class TestPeriodImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_period_dict(self, subject, test_admin_user):
        return {
            'pk': 1,
            'model': 'core.period',
            'admin_user_ids': [test_admin_user.id],
            'fields': {
                'short_name': 'testsemester',
                'start_time': '2017-02-14T11:04:46.585',
                'parentnode': subject.id,
                'long_name': 'Testsemester',
                'admins': [test_admin_user.id],
                'etag': '2017-05-15T11:04:46.585',
                'end_time': '2017-08-13T11:04:46.585'
            }
        }

    def test_import(self):
        test_admin_user = mommy.make(settings.AUTH_USER_MODEL)
        test_subject = mommy.make('core.Subject')
        self.create_v2dump(model_name='core.period',
                           data=self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user))
        periodimporter = PeriodImporter(input_root=self.temp_root_dir)
        periodimporter.import_models()
        self.assertEquals(Period.objects.count(), 1)

    def test_importer_pk(self):
        test_admin_user = mommy.make(settings.AUTH_USER_MODEL)
        test_subject = mommy.make('core.Subject')
        self.create_v2dump(model_name='core.period',
                           data=self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user))
        periodimporter = PeriodImporter(input_root=self.temp_root_dir)
        periodimporter.import_models()
        period = Period.objects.first()
        self.assertEquals(period.id, 1)

    def test_importer_short_name(self):
        test_admin_user = mommy.make(settings.AUTH_USER_MODEL)
        test_subject = mommy.make('core.Subject')
        self.create_v2dump(model_name='core.period',
                           data=self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user))
        periodimporter = PeriodImporter(input_root=self.temp_root_dir)
        periodimporter.import_models()
        period = Period.objects.first()
        self.assertEquals(period.short_name, 'testsemester')

    def test_importer_long_name(self):
        test_admin_user = mommy.make(settings.AUTH_USER_MODEL)
        test_subject = mommy.make('core.Subject')
        self.create_v2dump(model_name='core.period',
                           data=self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user))
        periodimporter = PeriodImporter(input_root=self.temp_root_dir)
        periodimporter.import_models()
        period = Period.objects.first()
        self.assertEquals(period.long_name, 'Testsemester')

    def test_importer_start_time(self):
        test_admin_user = mommy.make(settings.AUTH_USER_MODEL)
        test_subject = mommy.make('core.Subject')
        self.create_v2dump(model_name='core.period',
                           data=self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user))
        periodimporter = PeriodImporter(input_root=self.temp_root_dir)
        periodimporter.import_models()
        period = Period.objects.first()
        start_time = parse_datetime('2017-02-14T11:04:46.585')
        self.assertEquals(period.start_time, start_time)

    def test_importer_end_time(self):
        test_admin_user = mommy.make(settings.AUTH_USER_MODEL)
        test_subject = mommy.make('core.Subject')
        self.create_v2dump(model_name='core.period',
                           data=self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user))
        periodimporter = PeriodImporter(input_root=self.temp_root_dir)
        periodimporter.import_models()
        period = Period.objects.first()
        end_time = parse_datetime('2017-08-13T11:04:46.585')
        self.assertEquals(period.end_time, end_time)

    def test_importer_subject(self):
        test_admin_user = mommy.make(settings.AUTH_USER_MODEL)
        test_subject = mommy.make('core.Subject')
        self.create_v2dump(model_name='core.period',
                           data=self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user))
        periodimporter = PeriodImporter(input_root=self.temp_root_dir)
        periodimporter.import_models()
        period = Period.objects.first()
        self.assertEquals(period.parentnode, test_subject)

    def test_importer_permissiongroup_is_created(self):
        test_admin_user = mommy.make(settings.AUTH_USER_MODEL)
        test_subject = mommy.make('core.Subject')
        self.create_v2dump(model_name='core.period',
                           data=self._create_period_dict(subject=test_subject, test_admin_user=test_admin_user))
        periodimporter = PeriodImporter(input_root=self.temp_root_dir)
        periodimporter.import_models()
        self.assertEquals(Period.objects.count(), 1)
        period = Period.objects.first()
        self.assertEquals(account_models.PermissionGroup.objects.count(), 1)
        self.assertEquals(account_models.PermissionGroupUser.objects.count(), 1)
        self.assertEquals(account_models.PeriodPermissionGroup.objects.count(), 1)
        periods_for_admin_list = Period.objects.filter_user_is_admin(test_admin_user)
        self.assertEquals(len(periods_for_admin_list), 1)
        self.assertEquals(periods_for_admin_list[0], period)
