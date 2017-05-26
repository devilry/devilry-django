import pprint

from devilry.apps.core.models import Assignment, Period
from devilry.devilry_import_v2database import modelimporter


class AssignmentImporter(modelimporter.ModelImporter):
    def get_model_class(self):
        return Assignment

    def _get_period_from_parentnode_id(self, id):
        try:
            period = Period.objects.get(id=id)
        except Period.DoesNotExist:
            raise modelimporter.ModelImporterException(
                'No Period with id={} exists for imported Assignment'.format(id))
        return period

    def _get_new_grading_plugin_system_id(self, old_grading_system_plugin_id):
        if old_grading_system_plugin_id == 'devilry_gradingsystemplugin_approved':
            return Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED
        elif old_grading_system_plugin_id == 'devilry_gradingsystemplugin_points':
            return Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS

    def _get_new_anonymization_mode(self, anonymous):
        if anonymous:
            return Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS
        return Assignment.ANONYMIZATIONMODE_OFF

    def _create_assignment_from_object_dict(self, object_dict):
        assignment = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=assignment,
            object_dict=object_dict,
            attributes=[
                'pk',
                'long_name',
                'short_name',
                'publishing_time',
                'students_can_see_points',
                'first_deadline',
                'max_points',
                'delivery_types',
                'passing_grade_min_points',
                'scale_points_percent',
                'points_to_grade_mapper',
                'students_can_create_groups',
                'students_can_not_create_groups_after',
            ]
        )
        period = self._get_period_from_parentnode_id(id=object_dict['fields']['parentnode'])
        assignment.parentnode = period
        assignment.grading_system_plugin_id = self._get_new_grading_plugin_system_id(
            old_grading_system_plugin_id=object_dict['fields']['grading_system_plugin_id'])
        assignment.anonymizationmode = self._get_new_anonymization_mode(object_dict['fields']['anonymous'])
        assignment.full_clean()
        assignment.save()
        self.log_create(model_object=assignment, data=object_dict)

    def import_models(self, fake=False):
        directory_parser = self.v2assignment_directoryparser
        directory_parser.set_max_id_for_models_with_auto_generated_sequence_numbers(model_class=self.get_model_class())
        for object_dict in directory_parser.iterate_object_dicts():
            if fake:
                print('Would import: {}'.format(pprint.pformat(object_dict)))
            else:
                self._create_assignment_from_object_dict(object_dict=object_dict)

