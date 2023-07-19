import unittest

from django import test
from django.contrib.contenttypes.models import ContentType
from model_bakery import baker

from devilry.apps.core.models import Assignment
from devilry.devilry_import_v2database.modelimporters.assignment_importer import AssignmentImporter
from devilry.devilry_import_v2database.models import ImportedModel
from .importer_testcase_mixin import ImporterTestCaseMixin


@unittest.skip('Not relevant anymore, keep for history.')
class TestAssignmentImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_model_meta(self):
        return {
            'model_class_name': 'Assignment',
            'max_id': 12,
            'app_label': 'core'
        }

    def _create_assignment_dict(self, period, admin_user_ids_list=None):
        return {
            'pk': 6,
            'model': 'core.assignment',
            'admin_user_ids': admin_user_ids_list if admin_user_ids_list else [],
            'fields': {
                'examiners_publish_feedbacks_directly': True,
                'points_to_grade_mapper': 'raw-points',
                'short_name': 'week6',
                'students_can_create_groups': False,
                'students_can_see_points': True,
                'deadline_handling': 0,
                'publishing_time': '2016-05-16T11:04:59.577',
                'max_points': 2,
                'parentnode': period.id,
                'delivery_types': 0,
                'long_name': 'Week 6',
                'admins': admin_user_ids_list if admin_user_ids_list else [],
                'first_deadline': '2016-05-23T11:04:59.577',
                'passing_grade_min_points': 1,
                'anonymous': False,
                'students_can_not_create_groups_after': None,
                'grading_system_plugin_id': 'devilry_gradingsystemplugin_points',
                'scale_points_percent': 100
            }
        }

    def test_import(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(model_name='core.assignment',
                           data=self._create_assignment_dict(period=test_period))
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        self.assertEqual(Assignment.objects.count(), 1)

    def test_importer_pk(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(model_name='core.assignment',
                           data=self._create_assignment_dict(period=test_period))
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        assignment = Assignment.objects.first()
        self.assertEqual(assignment.pk, 6)
        self.assertEqual(assignment.id, 6)

    def test_importer_short_name(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(model_name='core.assignment',
                           data=self._create_assignment_dict(period=test_period))
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        assignment = Assignment.objects.first()
        self.assertEqual(assignment.short_name, 'week6')

    def test_importer_long_name(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(model_name='core.assignment',
                           data=self._create_assignment_dict(period=test_period))
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        assignment = Assignment.objects.first()
        self.assertEqual(assignment.long_name, 'Week 6')

    def test_importer_points_to_grade_mapper(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(model_name='core.assignment',
                           data=self._create_assignment_dict(period=test_period))
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        assignment = Assignment.objects.first()
        self.assertEqual(assignment.points_to_grade_mapper, Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS)

    def test_importer_students_can_create_groups(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(model_name='core.assignment',
                           data=self._create_assignment_dict(period=test_period))
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        assignment = Assignment.objects.first()
        self.assertFalse(assignment.students_can_create_groups)

    def test_importer_students_can_see_points(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(model_name='core.assignment',
                           data=self._create_assignment_dict(period=test_period))
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        assignment = Assignment.objects.first()
        self.assertTrue(assignment.students_can_see_points)

    def test_importer_delivery_handling(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(model_name='core.assignment',
                           data=self._create_assignment_dict(period=test_period))
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        assignment = Assignment.objects.first()
        self.assertEqual(assignment.deadline_handling, 0)

    def test_importer_max_points(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(model_name='core.assignment',
                           data=self._create_assignment_dict(period=test_period))
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        assignment = Assignment.objects.first()
        self.assertEqual(assignment.max_points, 2)

    def test_importer_delivery_types(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(model_name='core.assignment',
                           data=self._create_assignment_dict(period=test_period))
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        assignment = Assignment.objects.first()
        self.assertEqual(assignment.delivery_types, 0)

    def test_importer_passing_grade_min_points(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(model_name='core.assignment',
                           data=self._create_assignment_dict(period=test_period))
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        assignment = Assignment.objects.first()
        self.assertEqual(assignment.passing_grade_min_points, 1)

    def test_importer_anonymization_mode_anonymous_false(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(model_name='core.assignment',
                           data=self._create_assignment_dict(period=test_period))
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        assignment = Assignment.objects.first()
        self.assertEqual(assignment.anonymizationmode, Assignment.ANONYMIZATIONMODE_OFF)

    def test_importer_anonymization_mode_anonymous_true(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        assignment_data_dict = self._create_assignment_dict(period=test_period)
        assignment_data_dict['fields']['anonymous'] = True
        self.create_v2dump(model_name='core.assignment',
                           data=assignment_data_dict)
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        assignment = Assignment.objects.first()
        self.assertEqual(assignment.anonymizationmode, Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)

    def test_importer_grading_system_plugin_id_approved(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        assignment_data_dict = self._create_assignment_dict(period=test_period)
        assignment_data_dict['fields']['grading_system_plugin_id'] = 'devilry_gradingsystemplugin_approved'
        self.create_v2dump(model_name='core.assignment',
                           data=assignment_data_dict)
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        assignment = Assignment.objects.first()
        self.assertEqual(assignment.grading_system_plugin_id, Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED)

    def test_importer_grading_system_plugin_id_points(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(model_name='core.assignment',
                           data=self._create_assignment_dict(period=test_period))
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        assignment = Assignment.objects.first()
        self.assertEqual(assignment.grading_system_plugin_id, Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS)

    def test_importer_scale_points_percent(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(model_name='core.assignment',
                           data=self._create_assignment_dict(period=test_period))
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        assignment = Assignment.objects.first()
        self.assertEqual(assignment.scale_points_percent, 100)

    def test_importer_parentnode(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(model_name='core.assignment',
                           data=self._create_assignment_dict(period=test_period))
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        assignment = Assignment.objects.first()
        self.assertEqual(assignment.parentnode, test_period)

    def test_auto_sequence_numbered_objects_uses_meta_max_id(self):
        test_period = baker.make_recipe('devilry.apps.core.period_active')
        self.create_v2dump(model_name='core.assignment',
                           data=self._create_assignment_dict(period=test_period),
                           model_meta=self._create_model_meta())
        assignmentimporter = AssignmentImporter(input_root=self.temp_root_dir)
        assignmentimporter.import_models()
        self.assertEqual(Assignment.objects.count(), 1)
        assignment = Assignment.objects.first()
        self.assertEqual(assignment.pk, 6)
        self.assertEqual(assignment.id, 6)
        assignment_with_auto_id = baker.make('core.Assignment', parentnode=test_period)
        self.assertEqual(assignment_with_auto_id.pk, self._create_model_meta()['max_id']+1)
        self.assertEqual(assignment_with_auto_id.id, self._create_model_meta()['max_id']+1)
