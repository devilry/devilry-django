from django.contrib.contenttypes.models import ContentType

from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_import_v2database.models import ImportedModel
from django import test
from django.conf import settings
from django.utils.dateparse import parse_datetime

from model_mommy import mommy

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_import_v2database.modelimporters.assignmentgroup_importer import AssignmentGroupImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


class TestAssignmentGroupImporter(ImporterTestCaseMixin, test.TestCase):
    def setUp(self):
        super(TestAssignmentGroupImporter, self).setUp()
        AssignmentGroupDbCacheCustomSql().initialize()

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
        test_assignment = mommy.make('core.Assignment')
        self.create_v2dump(model_name='core.assignmentgroup',
                           data=self._create_assignmentgroup_dict(assignment=test_assignment))
        group_importer = AssignmentGroupImporter(input_root=self.temp_root_dir)
        group_importer.import_models()
        self.assertEquals(AssignmentGroup.objects.count(), 1)
        self.assertEquals(FeedbackSet.objects.count(), 1)

    def test_importer_pk(self):
        test_assignment = mommy.make('core.Assignment')
        self.create_v2dump(model_name='core.assignmentgroup',
                           data=self._create_assignmentgroup_dict(assignment=test_assignment))
        group_importer = AssignmentGroupImporter(input_root=self.temp_root_dir)
        group_importer.import_models()
        group = AssignmentGroup.objects.first()
        self.assertEquals(group.pk, 1)
        self.assertEquals(group.id, 1)

    def test_importer_name(self):
        test_assignment = mommy.make('core.Assignment')
        self.create_v2dump(model_name='core.assignmentgroup',
                           data=self._create_assignmentgroup_dict(assignment=test_assignment))
        group_importer = AssignmentGroupImporter(input_root=self.temp_root_dir)
        group_importer.import_models()
        group = AssignmentGroup.objects.first()
        self.assertEquals(group.name, 'Test AssignmentGroup')

    def test_importer_is_open(self):
        test_assignment = mommy.make('core.Assignment')
        self.create_v2dump(model_name='core.assignmentgroup',
                           data=self._create_assignmentgroup_dict(assignment=test_assignment))
        group_importer = AssignmentGroupImporter(input_root=self.temp_root_dir)
        group_importer.import_models()
        group = AssignmentGroup.objects.first()
        self.assertFalse(group.is_open)

    def test_importer_parentnode(self):
        test_assignment = mommy.make('core.Assignment')
        self.create_v2dump(model_name='core.assignmentgroup',
                           data=self._create_assignmentgroup_dict(assignment=test_assignment))
        group_importer = AssignmentGroupImporter(input_root=self.temp_root_dir)
        group_importer.import_models()
        group = AssignmentGroup.objects.first()
        self.assertEquals(group.parentnode, test_assignment)

    def test_importer_imported_model_created(self):
        test_assignment = mommy.make('core.Assignment')
        assignment_data_dict = self._create_assignmentgroup_dict(assignment=test_assignment)
        self.create_v2dump(model_name='core.assignmentgroup',
                           data=assignment_data_dict)
        group_importer = AssignmentGroupImporter(input_root=self.temp_root_dir)
        group_importer.import_models()
        group = AssignmentGroup.objects.first()
        self.assertEquals(ImportedModel.objects.count(), 1)
        imported_model = ImportedModel.objects.get(
            content_object_id=group.id,
            content_type=ContentType.objects.get_for_model(model=group)
        )
        self.assertEquals(imported_model.content_object, group)
        self.assertEquals(imported_model.data, assignment_data_dict)
