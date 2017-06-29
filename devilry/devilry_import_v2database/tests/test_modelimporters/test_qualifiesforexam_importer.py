from django import test
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_date

from model_mommy import mommy

from .importer_testcase_mixin import ImporterTestCaseMixin

from devilry.devilry_import_v2database.modelimporters.qualifiesforexam_importer import StatusImporter
from devilry.devilry_qualifiesforexam.models import Status


class TestStatusImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_model_meta(self, max_id):
        return {
            "model_class_name": "Status",
            "max_id": max_id,
            "app_label": "devilry_qualifiesforexam"
        }

    def _create_status_dict(self, period, user):
        return {
            "pk": 3,
            "model": "devilry_qualifiesforexam.status",
            "fields": {
                "status": "ready",
                "plugin": "devilry_qualifiesforexam_points",
                "period": period.id,
                "createtime": "2017-06-29T14:12:28.680",
                "user": user.id,
                "exported_timestamp": None,
                "message": ""
            }
        }

    def test_importer(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.status',
            data=self._create_status_dict(period=test_period, user=test_user)
        )
        status_importer = StatusImporter(input_root=self.temp_root_dir)
        status_importer.import_models()
        self.assertEquals(Status.objects.count(), 1)

    def test_importer_pk(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.status',
            data=self._create_status_dict(period=test_period, user=test_user)
        )
        status_importer = StatusImporter(input_root=self.temp_root_dir)
        status_importer.import_models()
        status = Status.objects.first()
        self.assertEquals(status.pk, 3)
        self.assertEquals(status.id, 3)

    # def test_importer_createtime(self):
    #     test_user = mommy.make(settings.AUTH_USER_MODEL)
    #     test_period = mommy.make_recipe('devilry.apps.core.period_active')
    #     self.create_v2dump(
    #         model_name='devilry_qualifiesforexam.status',
    #         data=self._create_status_dict(period=test_period, user=test_user)
    #     )
    #     status_importer = StatusImporter(input_root=self.temp_root_dir)
    #     status_importer.import_models()
    #     status = Status.objects.first()
    #     self.assertEquals(status.createtime, parse_date('2017-06-29 14:12:28.680'))

    def test_auto_sequence_numbered_objects_uses_meta_max_id(self):
        max_id = 10
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.status',
            data=self._create_status_dict(period=test_period, user=test_user),
            model_meta=self._create_model_meta(max_id=max_id)
        )
        status_importer = StatusImporter(input_root=self.temp_root_dir)
        status_importer.import_models()
        status = Status.objects.first()
        self.assertEquals(status.pk, 3)
        self.assertEquals(status.id, 3)
        status_with_auto_id = mommy.make('devilry_qualifiesforexam.Status', period=test_period, user=test_user)
        self.assertEquals(status_with_auto_id.pk, max_id+1)
        self.assertEquals(status_with_auto_id.id, max_id+1)
