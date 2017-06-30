from django import test
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_date

from model_mommy import mommy

from .importer_testcase_mixin import ImporterTestCaseMixin

from devilry.devilry_import_v2database.modelimporters.qualifiesforexam_importer import \
    StatusImporter, QualifiesForFinalExamImporter
from devilry.devilry_qualifiesforexam.models import Status, QualifiesForFinalExam
from devilry.devilry_qualifiesforexam_plugin_approved.plugin import SelectAssignmentsPlugin
from devilry.devilry_qualifiesforexam_plugin_students.plugin import StudentSelectPlugin
from devilry.devilry_qualifiesforexam_plugin_points.plugin import PointsPlugin


class TestStatusImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_model_meta(self, max_id):
        return {
            "model_class_name": "Status",
            "max_id": max_id,
            "app_label": "devilry_qualifiesforexam"
        }

    def _create_status_dict(self, period, user, plugin=None, status="ready"):
        return {
            "pk": 3,
            "model": "devilry_qualifiesforexam.status",
            "fields": {
                "status": status,
                "plugin": plugin if plugin else "devilry_qualifiesforexam_points",
                "period": period.id,
                "createtime": "2017-06-29T14:12:28.680",
                "user": user.id,
                "exported_timestamp": None,
                "message": "Message"
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

    def test_importer_status_ready(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.status',
            data=self._create_status_dict(period=test_period, user=test_user)
        )
        status_importer = StatusImporter(input_root=self.temp_root_dir)
        status_importer.import_models()
        status = Status.objects.first()
        self.assertEquals(status.status, Status.READY)

    def test_importer_status_othen_than_ready_is_set_to_notready(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.status',
            data=self._create_status_dict(period=test_period, user=test_user, status='somestatus')
        )
        status_importer = StatusImporter(input_root=self.temp_root_dir)
        status_importer.import_models()
        status = Status.objects.first()
        self.assertEquals(status.status, Status.NOTREADY)

    def test_importer_message(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.status',
            data=self._create_status_dict(period=test_period, user=test_user)
        )
        status_importer = StatusImporter(input_root=self.temp_root_dir)
        status_importer.import_models()
        status = Status.objects.first()
        self.assertEquals(status.message, "Message")

    def test_importer_status_points_plugin(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.status',
            data=self._create_status_dict(period=test_period, user=test_user, plugin="devilry_qualifiesforexam_points")
        )
        status_importer = StatusImporter(input_root=self.temp_root_dir)
        status_importer.import_models()
        status = Status.objects.first()
        self.assertEquals(status.plugin, PointsPlugin.plugintypeid)

    def test_importer_status_approved_all_plugin(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.status',
            data=self._create_status_dict(period=test_period, user=test_user,
                                          plugin='devilry_qualifiesforexam_approved.all')
        )
        status_importer = StatusImporter(input_root=self.temp_root_dir)
        status_importer.import_models()
        status = Status.objects.first()
        self.assertEquals(status.plugin, SelectAssignmentsPlugin.plugintypeid)

    def test_importer_status_approved_subset_plugin(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.status',
            data=self._create_status_dict(period=test_period, user=test_user,
                                          plugin='devilry_qualifiesforexam_approved.subset')
        )
        status_importer = StatusImporter(input_root=self.temp_root_dir)
        status_importer.import_models()
        status = Status.objects.first()
        self.assertEquals(status.plugin, SelectAssignmentsPlugin.plugintypeid)

    def test_import_status_select_students_plugin(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.status',
            data=self._create_status_dict(period=test_period, user=test_user,
                                          plugin='devilry_qualifiesforexam_select')
        )
        status_importer = StatusImporter(input_root=self.temp_root_dir)
        status_importer.import_models()
        status = Status.objects.first()
        self.assertEquals(status.plugin, StudentSelectPlugin.plugintypeid)

    def test_import_status_select_unknown_plugin(self):
        test_user = mommy.make(settings.AUTH_USER_MODEL)
        test_period = mommy.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.status',
            data=self._create_status_dict(period=test_period, user=test_user,
                                          plugin='devilry_qualifiesforexam_asd')
        )
        status_importer = StatusImporter(input_root=self.temp_root_dir)
        status_importer.import_models()
        status = Status.objects.first()
        self.assertEquals(status.plugin, 'Unknown Devilry V2 qualifiesforexam pluginid: devilry_qualifiesforexam_asd')

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


class TestQualifiesForFinalExamImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_model_meta(self, max_id):
        return {
            "model_class_name": "QualifiesForFinalExam",
            "max_id": max_id,
            "app_label": "devilry_qualifiesforexam"
        }

    def _create_status_dict(self, status, related_student, qualifies=None):
        return {
            "pk": 3,
            "model": "devilry_qualifiesforexam.qualifiesforfinalexam",
            "fields": {
                "relatedstudent": related_student.id,
                "status": status.id,
                "qualifies": qualifies
              }
        }

    def test_importer(self):
        test_relatedstudent = mommy.make('core.RelatedStudent')
        test_status = mommy.make('devilry_qualifiesforexam.Status')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.qualifiesforfinalexam',
            data=self._create_status_dict(status=test_status, related_student=test_relatedstudent)
        )
        QualifiesForFinalExamImporter(input_root=self.temp_root_dir).import_models()
        self.assertEquals(QualifiesForFinalExam.objects.count(), 1)

    def test_importer_pk(self):
        test_relatedstudent = mommy.make('core.RelatedStudent')
        test_status = mommy.make('devilry_qualifiesforexam.Status')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.qualifiesforfinalexam',
            data=self._create_status_dict(status=test_status, related_student=test_relatedstudent)
        )
        QualifiesForFinalExamImporter(input_root=self.temp_root_dir).import_models()
        qualifies = QualifiesForFinalExam.objects.first()
        self.assertEquals(qualifies.pk, 3)
        self.assertEquals(qualifies.id, 3)

    def test_importer_status(self):
        test_relatedstudent = mommy.make('core.RelatedStudent')
        test_status = mommy.make('devilry_qualifiesforexam.Status')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.qualifiesforfinalexam',
            data=self._create_status_dict(status=test_status, related_student=test_relatedstudent)
        )
        QualifiesForFinalExamImporter(input_root=self.temp_root_dir).import_models()
        qualifies = QualifiesForFinalExam.objects.first()
        self.assertEquals(qualifies.status, test_status)

    def test_importer_relatedstudent(self):
        test_relatedstudent = mommy.make('core.RelatedStudent')
        test_status = mommy.make('devilry_qualifiesforexam.Status')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.qualifiesforfinalexam',
            data=self._create_status_dict(status=test_status, related_student=test_relatedstudent)
        )
        QualifiesForFinalExamImporter(input_root=self.temp_root_dir).import_models()
        qualifies = QualifiesForFinalExam.objects.first()
        self.assertEquals(qualifies.relatedstudent, test_relatedstudent)

    def test_importer_qualifies_true(self):
        test_relatedstudent = mommy.make('core.RelatedStudent')
        test_status = mommy.make('devilry_qualifiesforexam.Status')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.qualifiesforfinalexam',
            data=self._create_status_dict(status=test_status, related_student=test_relatedstudent, qualifies=True)
        )
        QualifiesForFinalExamImporter(input_root=self.temp_root_dir).import_models()
        qualifies = QualifiesForFinalExam.objects.first()
        self.assertTrue(qualifies.qualifies)

    def test_importer_qualifies_false(self):
        test_relatedstudent = mommy.make('core.RelatedStudent')
        test_status = mommy.make('devilry_qualifiesforexam.Status')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.qualifiesforfinalexam',
            data=self._create_status_dict(status=test_status, related_student=test_relatedstudent, qualifies=False)
        )
        QualifiesForFinalExamImporter(input_root=self.temp_root_dir).import_models()
        qualifies = QualifiesForFinalExam.objects.first()
        self.assertFalse(qualifies.qualifies)

    def test_importer_qualifies_none(self):
        test_relatedstudent = mommy.make('core.RelatedStudent')
        test_status = mommy.make('devilry_qualifiesforexam.Status')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.qualifiesforfinalexam',
            data=self._create_status_dict(status=test_status, related_student=test_relatedstudent, qualifies=None)
        )
        QualifiesForFinalExamImporter(input_root=self.temp_root_dir).import_models()
        qualifies = QualifiesForFinalExam.objects.first()
        self.assertIsNone(qualifies.qualifies)

    def test_auto_sequence_numbered_objects_uses_meta_max_id(self):
        max_id = 10
        test_relatedstudent = mommy.make('core.RelatedStudent')
        test_status = mommy.make('devilry_qualifiesforexam.Status')
        self.create_v2dump(
            model_name='devilry_qualifiesforexam.qualifiesforfinalexam',
            data=self._create_status_dict(status=test_status, related_student=test_relatedstudent, qualifies=None),
            model_meta=self._create_model_meta(max_id=max_id)
        )
        QualifiesForFinalExamImporter(input_root=self.temp_root_dir).import_models()
        qualifies = QualifiesForFinalExam.objects.first()
        self.assertEquals(qualifies.pk, 3)
        self.assertEquals(qualifies.id, 3)
        qualifies_with_auto_id = mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam')
        self.assertEquals(qualifies_with_auto_id.pk, max_id+1)
        self.assertEquals(qualifies_with_auto_id.id, max_id+1)
