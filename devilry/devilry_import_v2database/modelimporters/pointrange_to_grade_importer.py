import pprint

from devilry.apps.core.models import PointToGradeMap, PointRangeToGrade, Assignment
from devilry.devilry_import_v2database import modelimporter
from devilry.devilry_import_v2database.modelimporters.modelimporter_utils import BulkCreator


class PointToGradeMapImporter(modelimporter.ModelImporter):
    def get_model_class(self):
        return PointToGradeMap

    def _get_assignment_from_assignment_id(self, id):
        try:
            assignment = Assignment.objects.get(id=id)
        except Assignment.DoesNotExist:
            raise modelimporter.ModelImporterException(
                'No Assignment with id={} exists for imported PointToGradeMap'.format(id))
        return assignment

    def _create_point_to_grade_map_from_object_dict(self, object_dict):
        point_to_grade_map = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=point_to_grade_map,
            object_dict=object_dict,
            attributes=[
                'pk',
                'invalid'
            ]
        )
        assignment = self._get_assignment_from_assignment_id(id=object_dict['fields']['assignment'])
        point_to_grade_map.assignment = assignment
        if self.should_clean():
            point_to_grade_map.full_clean()
        self.log_create(model_object=point_to_grade_map, data=object_dict)
        return point_to_grade_map

    def import_models(self, fake=False):
        directory_parser = self.v2pointtogrademap_directoryparser
        directory_parser.set_max_id_for_models_with_auto_generated_sequence_numbers(model_class=self.get_model_class())
        with BulkCreator(model_class=self.get_model_class()) as point_to_grade_map_bulk_creator:
            for object_dict in directory_parser.iterate_object_dicts():
                if fake:
                    print('Would import: {}'.format(pprint.pformat(object_dict)))
                else:
                    point_to_grade_map = self._create_point_to_grade_map_from_object_dict(object_dict=object_dict)
                    point_to_grade_map_bulk_creator.add(point_to_grade_map)


class PointRangeToGradeImporter(modelimporter.ModelImporter):
    def get_model_class(self):
        return PointRangeToGrade

    def _get_point_to_grade_map_from_point_to_grade_map_id(self, id):
        try:
            point_to_grade_map = PointToGradeMap.objects.get(id=id)
        except PointToGradeMap.DoesNotExist:
            raise modelimporter.ModelImporterException(
                'No PointToGradeMap with id={} exists for imported PointRangeToGrade'.format(id))
        return point_to_grade_map

    def _create_point_range_to_grade_from_object_dict(self, object_dict):
        point_range_to_grade = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=point_range_to_grade,
            object_dict=object_dict,
            attributes=[
                'pk',
                'minimum_points',
                'maximum_points',
                'grade'
            ]
        )
        point_to_grade_map = self._get_point_to_grade_map_from_point_to_grade_map_id(
            id=object_dict['fields']['point_to_grade_map'])
        point_range_to_grade.point_to_grade_map = point_to_grade_map
        if self.should_clean():
            point_range_to_grade.full_clean()
        self.log_create(model_object=point_range_to_grade, data=object_dict)
        return point_range_to_grade

    def import_models(self, fake=False):
        directory_parser = self.v2pointrangetograde_directoryparser
        directory_parser.set_max_id_for_models_with_auto_generated_sequence_numbers(model_class=self.get_model_class())
        with BulkCreator(model_class=self.get_model_class()) as point_range_to_grade_bulk_creator:
            for object_dict in directory_parser.iterate_object_dicts():
                if fake:
                    print('Would import: {}'.format(pprint.pformat(object_dict)))
                else:
                    point_range_to_grade = self._create_point_range_to_grade_from_object_dict(object_dict=object_dict)
                    point_range_to_grade_bulk_creator.add(point_range_to_grade)
