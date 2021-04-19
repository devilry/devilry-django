import unittest

from django import test
from model_bakery import baker

from devilry.apps.core.models import PointToGradeMap, Assignment
from devilry.devilry_import_v2database.modelimporters.pointrange_to_grade_importer import PointToGradeMapImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


@unittest.skip('Not relevant anymore, keep for history.')
class TestPointToGradeMapImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_model_meta(self):
        return {
            "model_class_name": "PointToGradeMap",
            "max_id": 7,
            "app_label": "core"
        }

    def _create_point_to_grade_map_dict(self, assignment, **field_kwargs):
        return {
            "pk": 3,
            "model": "core.pointtogrademap",
            "fields": {
                "assignment": assignment.id,
                "invalid": field_kwargs.get('invalid', False)
            }
        }

    def __make_assignment(self, **assignment_kwargs):
        return baker.make('core.Assignment',
                          points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE,
                          grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS,
                          **assignment_kwargs)

    def test_import(self):
        imported_assignment = self.__make_assignment()
        self.create_v2dump(model_name='core.pointtogrademap',
                           data=self._create_point_to_grade_map_dict(assignment=imported_assignment),
                           model_meta=self._create_model_meta())
        grademapimporter = PointToGradeMapImporter(input_root=self.temp_root_dir)
        self.assertEqual(PointToGradeMap.objects.count(), 0)
        grademapimporter.import_models()
        self.assertEqual(PointToGradeMap.objects.count(), 1)

    def test_importer_pk(self):
        imported_assignment = self.__make_assignment()
        self.create_v2dump(model_name='core.pointtogrademap',
                           data=self._create_point_to_grade_map_dict(assignment=imported_assignment),
                           model_meta=self._create_model_meta())
        grademapimporter = PointToGradeMapImporter(input_root=self.temp_root_dir)
        grademapimporter.import_models()
        self.assertEqual(PointToGradeMap.objects.get().pk, 3)
        self.assertEqual(PointToGradeMap.objects.get().id, 3)

    def test_importer_field_assignment(self):
        imported_assignment = self.__make_assignment()
        self.create_v2dump(model_name='core.pointtogrademap',
                           data=self._create_point_to_grade_map_dict(assignment=imported_assignment),
                           model_meta=self._create_model_meta())
        grademapimporter = PointToGradeMapImporter(input_root=self.temp_root_dir)
        grademapimporter.import_models()
        self.assertEqual(PointToGradeMap.objects.get().assignment, imported_assignment)

    def test_importer_field_invalid_true(self):
        imported_assignment = self.__make_assignment()
        self.create_v2dump(model_name='core.pointtogrademap',
                           data=self._create_point_to_grade_map_dict(assignment=imported_assignment, invalid=True),
                           model_meta=self._create_model_meta())
        grademapimporter = PointToGradeMapImporter(input_root=self.temp_root_dir)
        grademapimporter.import_models()
        self.assertTrue(PointToGradeMap.objects.get().invalid)

    def test_importer_field_invalid_false(self):
        imported_assignment = self.__make_assignment()
        self.create_v2dump(model_name='core.pointtogrademap',
                           data=self._create_point_to_grade_map_dict(assignment=imported_assignment),
                           model_meta=self._create_model_meta())
        grademapimporter = PointToGradeMapImporter(input_root=self.temp_root_dir)
        grademapimporter.import_models()
        self.assertFalse(PointToGradeMap.objects.get().invalid)

    def test_import_multiple_grade_maps(self):
        imported_assignment1 = self.__make_assignment()
        imported_assignment2 = self.__make_assignment()
        imported_assignment3 = self.__make_assignment()

        # Create PointToGradeMap dict and import for imported_assignment1
        grade_map_dict1 = self._create_point_to_grade_map_dict(
            assignment=imported_assignment1)
        grade_map_dict1['pk'] = 1
        self.create_v2dump(model_name='core.pointtogrademap', data=grade_map_dict1)
        PointToGradeMapImporter(input_root=self.temp_root_dir).import_models()

        # Create PointToGradeMap dict and import for imported_assignment2
        grade_map_dict2 = self._create_point_to_grade_map_dict(
            assignment=imported_assignment2)
        grade_map_dict2['pk'] = 2
        self.create_v2dump(model_name='core.pointtogrademap', data=grade_map_dict2)
        PointToGradeMapImporter(input_root=self.temp_root_dir).import_models()

        # Create PointToGradeMap dict and import for imported_assignment3
        grade_map_dict3 = self._create_point_to_grade_map_dict(
            assignment=imported_assignment3)
        self.create_v2dump(model_name='core.pointtogrademap', data=grade_map_dict3)
        PointToGradeMapImporter(input_root=self.temp_root_dir).import_models()

        self.assertEqual(PointToGradeMap.objects.count(), 3)
        grade_maps = PointToGradeMap.objects.all().order_by('assignment_id')
        imported_assignment1_grade_map = grade_maps[0]
        imported_assignment2_grade_map = grade_maps[1]
        imported_assignment3_grade_map = grade_maps[2]

        self.assertEqual(imported_assignment1_grade_map.pk, 1)
        self.assertEqual(imported_assignment1_grade_map.assignment_id,
                         Assignment.objects.get(id=imported_assignment1.id).id)
        self.assertFalse(imported_assignment1_grade_map.invalid)

        self.assertEqual(imported_assignment2_grade_map.pk, 2)
        self.assertEqual(imported_assignment2_grade_map.assignment_id,
                         Assignment.objects.get(id=imported_assignment2.id).id)
        self.assertFalse(imported_assignment2_grade_map.invalid)

        self.assertEqual(imported_assignment3_grade_map.pk, 3)
        self.assertEqual(imported_assignment3_grade_map.assignment_id,
                         Assignment.objects.get(id=imported_assignment3.id).id)
        self.assertFalse(imported_assignment3_grade_map.invalid)

    def test_auto_sequence_numbered_objects_uses_meta_max_id(self):
        imported_assignment = self.__make_assignment()
        self.create_v2dump(model_name='core.pointtogrademap',
                           data=self._create_point_to_grade_map_dict(assignment=imported_assignment),
                           model_meta=self._create_model_meta())
        grademapimporter = PointToGradeMapImporter(input_root=self.temp_root_dir)
        grademapimporter.import_models()
        self.assertEqual(PointToGradeMap.objects.count(), 1)
        grade_map = PointToGradeMap.objects.first()
        self.assertEqual(grade_map.pk, 3)
        self.assertEqual(grade_map.id, 3)
        grade_map_with_auto_id = baker.make('core.PointToGradeMap')
        self.assertEqual(grade_map_with_auto_id.pk, self._create_model_meta()['max_id']+1)
        self.assertEqual(grade_map_with_auto_id.id, self._create_model_meta()['max_id']+1)