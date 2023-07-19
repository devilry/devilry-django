import unittest

from django.contrib.contenttypes.models import ContentType

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_import_v2database.models import ImportedModel
from django import test
from django.conf import settings
from django.utils.dateparse import parse_datetime

from model_bakery import baker

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_import_v2database.modelimporters.assignmentgroup_importer import AssignmentGroupImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


@unittest.skip('Not relevant anymore, keep for history.')
class TestAssignmentGroupImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_model_meta(self):
        return {
            'model_class_name': 'bAssignmentGroup',
            'max_id': 156,
            'app_label': 'core'
        }

    def _create_assignmentgroup_dict(self, assignment):
        return {
            'pk': 1,
            'model':
                'core.assignmentgroup',
            'fields': {
                'last_deadline': 1,
                'name': 'Test AssignmentGroup',
                'parentnode': assignment.id,
                'etag': '2017-05-15T11:04:46.679',
                'is_open': False,
                'delivery_status': 'corrected',
                'feedback': 1
            }
        }

    def test_importer(self):
        test_assignment = baker.make('core.Assignment')
        self.create_v2dump(model_name='core.assignmentgroup',
                           data=self._create_assignmentgroup_dict(assignment=test_assignment))
        group_importer = AssignmentGroupImporter(input_root=self.temp_root_dir)
        group_importer.import_models()
        self.assertEqual(AssignmentGroup.objects.count(), 1)
        self.assertEqual(FeedbackSet.objects.count(), 0)

    def test_importer_pk(self):
        test_assignment = baker.make('core.Assignment')
        self.create_v2dump(model_name='core.assignmentgroup',
                           data=self._create_assignmentgroup_dict(assignment=test_assignment))
        group_importer = AssignmentGroupImporter(input_root=self.temp_root_dir)
        group_importer.import_models()
        group = AssignmentGroup.objects.first()
        self.assertEqual(group.pk, 1)
        self.assertEqual(group.id, 1)

    def test_importer_name(self):
        test_assignment = baker.make('core.Assignment')
        self.create_v2dump(model_name='core.assignmentgroup',
                           data=self._create_assignmentgroup_dict(assignment=test_assignment))
        group_importer = AssignmentGroupImporter(input_root=self.temp_root_dir)
        group_importer.import_models()
        group = AssignmentGroup.objects.first()
        self.assertEqual(group.name, 'Test AssignmentGroup')

    def test_importer_is_open(self):
        test_assignment = baker.make('core.Assignment')
        self.create_v2dump(model_name='core.assignmentgroup',
                           data=self._create_assignmentgroup_dict(assignment=test_assignment))
        group_importer = AssignmentGroupImporter(input_root=self.temp_root_dir)
        group_importer.import_models()
        group = AssignmentGroup.objects.first()
        self.assertFalse(group.is_open)

    def test_importer_parentnode(self):
        test_assignment = baker.make('core.Assignment')
        self.create_v2dump(model_name='core.assignmentgroup',
                           data=self._create_assignmentgroup_dict(assignment=test_assignment))
        group_importer = AssignmentGroupImporter(input_root=self.temp_root_dir)
        group_importer.import_models()
        group = AssignmentGroup.objects.first()
        self.assertEqual(group.parentnode, test_assignment)

    def test_auto_sequence_numbered_objects_uses_meta_max_id(self):
        test_assignment = baker.make('core.Assignment')
        self.create_v2dump(model_name='core.assignmentgroup',
                           data=self._create_assignmentgroup_dict(assignment=test_assignment),
                           model_meta=self._create_model_meta())
        group_importer = AssignmentGroupImporter(input_root=self.temp_root_dir)
        group_importer.import_models()
        self.assertEqual(AssignmentGroup.objects.count(), 1)
        group = AssignmentGroup.objects.first()
        self.assertEqual(group.pk, 1)
        self.assertEqual(group.id, 1)
        group_with_auto_id = baker.make('core.AssignmentGroup', parentnode=test_assignment)
        self.assertEqual(group_with_auto_id.pk, self._create_model_meta()['max_id']+1)
        self.assertEqual(group_with_auto_id.id, self._create_model_meta()['max_id']+1)
