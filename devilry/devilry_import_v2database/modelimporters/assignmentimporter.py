import pprint

from devilry.apps.core.models import Assignment
from devilry.devilry_account import models as account_models
from devilry.devilry_import_v2database import modelimporter


class AssignmentImporter(modelimporter.ModelImporter):
    def get_model_class(self):
        return Assignment

    def _create_assignment_from_object_dict(self, object_dict):
        assignment = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=assignment,
            object_dict=object_dict,
            attributes=[
                'pk',
                'long_name',
                'short_name',
                'start_time',
                'end_time',
            ]
        )
        assignment.full_clean()
        assignment.save()
        self.log_create(model_object=assignment, data=object_dict)

    def import_models(self, fake=False):
        for object_dict in self.v2assignment_directoryparser.iterate_object_dicts():
            if fake:
                print('Would import: {}'.format(pprint.pformat(object_dict)))
            else:
                self._create_assignment_from_object_dict(object_dict=object_dict)

