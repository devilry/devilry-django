import unittest

from django import test
from model_bakery import baker

from devilry.apps.core.models import PointToGradeMap, PointRangeToGrade, Assignment
from devilry.devilry_import_v2database.modelimporters.pointrange_to_grade_importer import PointRangeToGradeImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


@unittest.skip('Not relevant anymore, keep for history.')
class TestPointRangeToGradeMapImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_model_meta(self):
        return {
            "model_class_name": "PointRangeToGrade",
            "max_id": 10,
            "app_label": "core"
        }

    def _create_point_range_to_grade_map_dict(self, point_to_grade_map, pk=1, **field_kwargs):
        return {
            "pk": pk,
            "model": "core.pointrangetograde",
            "fields": {
                "minimum_points": field_kwargs.get('minimum_points', 0),
                "grade": field_kwargs.get('grade', 'F'),
                "point_to_grade_map": point_to_grade_map.id,
                "maximum_points": field_kwargs.get('maximum_points', 10)
            }
        }

    def _create_point_range_to_grade_map_dicts_default(self, point_to_grade_map):
        return [
            self._create_point_range_to_grade_map_dict(
                point_to_grade_map=point_to_grade_map,
                pk=1, minimum_points=0, maximum_points=19, grade='F'),
            self._create_point_range_to_grade_map_dict(
                point_to_grade_map=point_to_grade_map,
                pk=2, minimum_points=20, maximum_points=39, grade='E'),
            self._create_point_range_to_grade_map_dict(
                point_to_grade_map=point_to_grade_map,
                pk=3, minimum_points=40, maximum_points=59, grade='D'),
            self._create_point_range_to_grade_map_dict(
                point_to_grade_map=point_to_grade_map,
                pk=4, minimum_points=60, maximum_points=79, grade='C'),
            self._create_point_range_to_grade_map_dict(
                point_to_grade_map=point_to_grade_map,
                pk=5, minimum_points=80, maximum_points=94, grade='B'),
            self._create_point_range_to_grade_map_dict(
                point_to_grade_map=point_to_grade_map,
                pk=6, minimum_points=95, maximum_points=100, grade='A'),
        ]

    def __make_point_to_grade_map(self, **point_to_grade_map_kwargs):
        assignment = baker.make('core.Assignment',
                                points_to_grade_mapper=Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE,
                                grading_system_plugin_id=Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)
        return baker.make('core.PointToGradeMap',
                          assignment=assignment,
                          **point_to_grade_map_kwargs)

    def test_importer(self):
        imported_point_to_grade_map = self.__make_point_to_grade_map()
        self.create_v2dump(model_name='core.pointrangetograde',
                           data=self._create_point_range_to_grade_map_dict(
                               point_to_grade_map=imported_point_to_grade_map),
                           model_meta=self._create_model_meta())
        self.assertEqual(PointRangeToGrade.objects.count(), 0)
        PointRangeToGradeImporter(input_root=self.temp_root_dir).import_models()
        self.assertEqual(PointRangeToGrade.objects.count(), 1)

    def test_importer_pk(self):
        imported_point_to_grade_map = self.__make_point_to_grade_map()
        self.create_v2dump(model_name='core.pointrangetograde',
                           data=self._create_point_range_to_grade_map_dict(
                               point_to_grade_map=imported_point_to_grade_map, pk=3),
                           model_meta=self._create_model_meta())
        PointRangeToGradeImporter(input_root=self.temp_root_dir).import_models()
        self.assertEqual(PointRangeToGrade.objects.get().pk, 3)
        self.assertEqual(PointRangeToGrade.objects.get().id, 3)

    def test_importer_point_to_grade_map(self):
        imported_point_to_grade_map = self.__make_point_to_grade_map()
        self.create_v2dump(model_name='core.pointrangetograde',
                           data=self._create_point_range_to_grade_map_dict(
                               point_to_grade_map=imported_point_to_grade_map),
                           model_meta=self._create_model_meta())
        PointRangeToGradeImporter(input_root=self.temp_root_dir).import_models()
        self.assertEqual(PointRangeToGrade.objects.get().point_to_grade_map_id, imported_point_to_grade_map.id)

    def test_importer_field_minimum_points(self):
        imported_point_to_grade_map = self.__make_point_to_grade_map()
        self.create_v2dump(model_name='core.pointrangetograde',
                           data=self._create_point_range_to_grade_map_dict(
                               point_to_grade_map=imported_point_to_grade_map, minimum_points=5),
                           model_meta=self._create_model_meta())
        PointRangeToGradeImporter(input_root=self.temp_root_dir).import_models()
        self.assertEqual(PointRangeToGrade.objects.get().minimum_points, 5)

    def test_importer_field_maximum_points(self):
        imported_point_to_grade_map = self.__make_point_to_grade_map()
        self.create_v2dump(model_name='core.pointrangetograde',
                           data=self._create_point_range_to_grade_map_dict(
                               point_to_grade_map=imported_point_to_grade_map, maximum_points=42),
                           model_meta=self._create_model_meta())
        PointRangeToGradeImporter(input_root=self.temp_root_dir).import_models()
        self.assertEqual(PointRangeToGrade.objects.get().maximum_points, 42)

    def test_importer_field_grade(self):
        imported_point_to_grade_map = self.__make_point_to_grade_map()
        self.create_v2dump(model_name='core.pointrangetograde',
                           data=self._create_point_range_to_grade_map_dict(
                               point_to_grade_map=imported_point_to_grade_map, grade='C'),
                           model_meta=self._create_model_meta())
        PointRangeToGradeImporter(input_root=self.temp_root_dir).import_models()
        self.assertEqual(PointRangeToGrade.objects.get().grade, 'C')

    def test_importer_all_fields(self):
        imported_point_to_grade_map = self.__make_point_to_grade_map()
        self.create_v2dump(model_name='core.pointrangetograde',
                           data=self._create_point_range_to_grade_map_dict(
                               point_to_grade_map=imported_point_to_grade_map,
                               minimum_points=60,
                               maximum_points=79,
                               grade='C'),
                           model_meta=self._create_model_meta())
        PointRangeToGradeImporter(input_root=self.temp_root_dir).import_models()
        self.assertEqual(PointRangeToGrade.objects.get().minimum_points, 60)
        self.assertEqual(PointRangeToGrade.objects.get().maximum_points, 79)
        self.assertEqual(PointRangeToGrade.objects.get().grade, 'C')

    def test_not_assigned_to_wrong_point_to_grade_map(self):
        imported_point_to_grade_map1 = self.__make_point_to_grade_map()
        imported_point_to_grade_map2 = self.__make_point_to_grade_map()
        self.create_v2dump(model_name='core.pointrangetograde',
                           data=self._create_point_range_to_grade_map_dict(
                               point_to_grade_map=imported_point_to_grade_map2),
                           model_meta=self._create_model_meta())
        PointRangeToGradeImporter(input_root=self.temp_root_dir).import_models()
        self.assertNotEqual(PointRangeToGrade.objects.get().point_to_grade_map_id, imported_point_to_grade_map1.id)
        self.assertEqual(PointRangeToGrade.objects.get().point_to_grade_map_id, imported_point_to_grade_map2.id)

    def test_importer_complete_table(self):
        imported_point_to_grade_map = self.__make_point_to_grade_map()
        grade_range_dict_list = self._create_point_range_to_grade_map_dicts_default(
            point_to_grade_map=imported_point_to_grade_map)
        for grade_range_dict in grade_range_dict_list:
            self.create_v2dump(model_name='core.pointrangetograde',
                               data=grade_range_dict,
                               model_meta=self._create_model_meta())
            PointRangeToGradeImporter(input_root=self.temp_root_dir).import_models()
        self.assertEqual(PointRangeToGrade.objects.count(), 6)
        point_range_f = PointRangeToGrade.objects.get(grade='F')
        point_range_e = PointRangeToGrade.objects.get(grade='E')
        point_range_d = PointRangeToGrade.objects.get(grade='D')
        point_range_c = PointRangeToGrade.objects.get(grade='C')
        point_range_b = PointRangeToGrade.objects.get(grade='B')
        point_range_a = PointRangeToGrade.objects.get(grade='A')

        self.assertEqual(point_range_f.point_to_grade_map_id, imported_point_to_grade_map.id)
        self.assertEqual(point_range_f.minimum_points, 0)
        self.assertEqual(point_range_f.maximum_points, 19)

        self.assertEqual(point_range_e.point_to_grade_map_id, imported_point_to_grade_map.id)
        self.assertEqual(point_range_e.minimum_points, 20)
        self.assertEqual(point_range_e.maximum_points, 39)

        self.assertEqual(point_range_d.point_to_grade_map_id, imported_point_to_grade_map.id)
        self.assertEqual(point_range_d.minimum_points, 40)
        self.assertEqual(point_range_d.maximum_points, 59)

        self.assertEqual(point_range_c.point_to_grade_map_id, imported_point_to_grade_map.id)
        self.assertEqual(point_range_c.minimum_points, 60)
        self.assertEqual(point_range_c.maximum_points, 79)

        self.assertEqual(point_range_b.point_to_grade_map_id, imported_point_to_grade_map.id)
        self.assertEqual(point_range_b.minimum_points, 80)
        self.assertEqual(point_range_b.maximum_points, 94)

        self.assertEqual(point_range_a.point_to_grade_map_id, imported_point_to_grade_map.id)
        self.assertEqual(point_range_a.minimum_points, 95)
        self.assertEqual(point_range_a.maximum_points, 100)

    def test_auto_sequence_numbered_objects_uses_meta_max_id(self):
        imported_point_to_grade_map = self.__make_point_to_grade_map()
        self.create_v2dump(model_name='core.pointrangetograde',
                           data=self._create_point_range_to_grade_map_dict(
                               point_to_grade_map=imported_point_to_grade_map, pk=3),
                           model_meta=self._create_model_meta())
        PointRangeToGradeImporter(input_root=self.temp_root_dir).import_models()
        self.assertEqual(PointRangeToGrade.objects.count(), 1)
        self.assertEqual(PointRangeToGrade.objects.get().pk, 3)
        self.assertEqual(PointRangeToGrade.objects.get().id, 3)
        point_range_to_grade = baker.make('core.PointRangeToGrade')
        self.assertEqual(point_range_to_grade.pk, self._create_model_meta()['max_id']+1)
        self.assertEqual(point_range_to_grade.id, self._create_model_meta()['max_id']+1)
