import pprint

from django.contrib.auth import get_user_model

from devilry.apps.core import models as core_models
from devilry.devilry_import_v2database import modelimporter
from devilry.devilry_qualifiesforexam import models
from devilry.devilry_qualifiesforexam_plugin_approved import plugin as approved_plugin
from devilry.devilry_qualifiesforexam_plugin_points import plugin as points_plugin
from devilry.devilry_qualifiesforexam_plugin_students import plugin as students_plugin
from devilry.devilry_import_v2database.modelimporters.modelimporter_utils import BulkCreator


class StatusImporter(modelimporter.ModelImporter):
    def get_model_class(self):
        return models.Status

    def _get_period_from_id(self, period_id):
        try:
            period = core_models.Period.objects.get(id=period_id)
        except core_models.Period.DoesNotExist:
            raise modelimporter.ModelImporterException(
                'Period with id {} does not exist'.format(period_id)
            )
        return period

    def _get_user_from_id(self, user_id):
        try:
            user = get_user_model().objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            raise modelimporter.ModelImporterException(
                'User with id {} does not exist'.format(user_id)
            )
        return user

    def _get_status(self, v2_status):
        if v2_status == 'ready':
            return models.Status.READY
        return models.Status.NOTREADY

    def _get_plugin_id(self, v2_pluginid):
        """
        Get v3 plugintypeid from v2 pluginid
        """
        if v2_pluginid == 'devilry_qualifiesforexam_approved.all':
            return approved_plugin.SelectAssignmentsPlugin.plugintypeid
        if v2_pluginid == 'devilry_qualifiesforexam_approved.subset':
            return approved_plugin.SelectAssignmentsPlugin.plugintypeid
        if v2_pluginid == 'devilry_qualifiesforexam_points':
            return points_plugin.PointsPlugin.plugintypeid
        if v2_pluginid == 'devilry_qualifiesforexam_select':
            return students_plugin.StudentSelectPlugin.plugintypeid
        return 'Unknown Devilry V2 qualifiesforexam pluginid: {}'.format(v2_pluginid)

    def _create_status_from_object_dict(self, object_dict):
        status = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=status,
            object_dict=object_dict,
            attributes=[
                'pk',
                'createtime',
                'exported_timestamp',
                'message',
                # 'status',
            ]
        )
        status.user = self._get_user_from_id(user_id=object_dict['fields']['user'])
        status.period = self._get_period_from_id(period_id=object_dict['fields']['period'])
        status.plugin = self._get_plugin_id(v2_pluginid=object_dict['fields']['plugin'])
        status.status = self._get_status(v2_status=object_dict['fields']['status'])
        if self.should_clean():
            status.full_clean()
        self.log_create(model_object=status, data=object_dict)
        return status

    def import_models(self, fake=False):
        directory_parser = self.v2qualifiesforexam_status_directoryparser
        directory_parser.set_max_id_for_models_with_auto_generated_sequence_numbers(model_class=self.get_model_class())
        with BulkCreator(model_class=self.get_model_class()) as status_bulk_creator:
            for object_dict in directory_parser.iterate_object_dicts():
                if fake:
                    print(('Would import: {}'.format(pprint.pformat(object_dict))))
                else:
                    status = self._create_status_from_object_dict(object_dict=object_dict)
                    status_bulk_creator.add(status)


class QualifiesForFinalExamImporter(modelimporter.ModelImporter):
    def get_model_class(self):
        return models.QualifiesForFinalExam

    def _get_related_student_from_id(self, related_student_id):
        try:
            related_student = core_models.RelatedStudent.objects.get(id=related_student_id)
        except core_models.RelatedStudent.DoesNotExist:
            raise modelimporter.ModelImporterException(
                'RelatedStudent with id {} does not exist'.format(related_student_id)
            )
        return related_student

    def _get_status_from_id(self, status_id):
        try:
            status = models.Status.objects.get(id=status_id)
        except models.Status.DoesNotExist:
            raise modelimporter.ModelImporterException(
                'QualifiesForExam Status with id {} does not exist'.format(status_id)
            )
        return status

    def _create_qualifiesforfinalexam_from_object_dict(self, object_dict):
        qualifies_for_final_exam = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=qualifies_for_final_exam,
            object_dict=object_dict,
            attributes=[
                'pk',
                'qualifies'
            ]
        )
        qualifies_for_final_exam.relatedstudent = self._get_related_student_from_id(
            object_dict['fields']['relatedstudent']
        )
        qualifies_for_final_exam.status = self._get_status_from_id(object_dict['fields']['status'])
        if self.should_clean():
            qualifies_for_final_exam.full_clean()
        self.log_create(model_object=qualifies_for_final_exam, data=object_dict)
        return qualifies_for_final_exam

    def import_models(self, fake=False):
        directory_parser = self.v2qualifiesforexamfinalexam_directoryparser
        directory_parser.set_max_id_for_models_with_auto_generated_sequence_numbers(model_class=self.get_model_class())
        with BulkCreator(model_class=self.get_model_class()) as qualifies_bulk_creator:
            for object_dict in directory_parser.iterate_object_dicts():
                if fake:
                    print(('Would import: {}'.format(pprint.pformat(object_dict))))
                else:
                    qualifies_for_final_exam = self._create_qualifiesforfinalexam_from_object_dict(object_dict=object_dict)
                    qualifies_bulk_creator.add(qualifies_for_final_exam)
