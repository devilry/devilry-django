import pprint

from devilry.apps.core.models import Assignment

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_import_v2database import modelimporter


class AssignmentGroupImporter(modelimporter.ModelImporter):
    def get_model_class(self):
        return AssignmentGroup

    def _get_assignment_from_parentnode_id(self, id):
        try:
            assignment = Assignment.objects.get(id=id)
        except Assignment.DoesNotExist:
            raise modelimporter.ModelImporterException(
                'No Assignment with id={} exists for imported AssignmentGroup'.format(id))
        return assignment

    def _create_assignmentgroup_from_object_dict(self, object_dict):
        assignment_group = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=assignment_group,
            object_dict=object_dict,
            attributes=[
                'pk',
                'name',
                'is_open',
            ]
        )
        assignment = self._get_assignment_from_parentnode_id(id=object_dict['fields']['parentnode'])
        assignment_group.parentnode = assignment
        assignment_group.full_clean()
        assignment_group.save()
        self.log_create(model_object=assignment_group, data=object_dict)

    def import_models(self, fake=False):
        directory_parser = self.v2assignmentgroup_directoryparser
        directory_parser.set_max_id_for_models_with_auto_generated_sequence_numbers(model_class=self.get_model_class())
        for object_dict in directory_parser.iterate_object_dicts():
            if fake:
                print('Would import: {}'.format(pprint.pformat(object_dict)))
            else:
                self._create_assignmentgroup_from_object_dict(object_dict=object_dict)
