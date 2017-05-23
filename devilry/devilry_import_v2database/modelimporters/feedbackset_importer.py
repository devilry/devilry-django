import pprint

from django.contrib.auth import get_user_model

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_import_v2database import modelimporter
from devilry.devilry_import_v2database.models import ImportedModel


class FeedbackSetImporter(modelimporter.ModelImporter):
    def get_model_class(self):
        return FeedbackSet

    def _get_assignment_group_from_id(self, assignment_group_id):
        try:
            assignment_group = AssignmentGroup.objects.get(id=assignment_group_id)
        except AssignmentGroup.DoesNotExist:
            raise modelimporter.ModelImporterException(
                'No AssignmentGroup with id {} was found.'.format(assignment_group_id))
        return assignment_group

    def _only_feedback_set_first_attempt_has_been_added(self):
        """
        Checking imported models if a FeedbackSet has already been added.
        """
        pass

    def _create_feedback_set_from_object_dict(self, object_dict):
        feedback_set = self.get_model_class()()

    def import_models(self, fake=False):
        for object_dict in self.v2deadline_directoryparser.iterate_object_dicts():
            if fake:
                print('Would import: {}'.format(pprint.pformat(object_dict)))
            else:
                self._create_feedback_set_from_object_dict(object_dict=object_dict)
