import pprint

from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_import_v2database import modelimporter
from devilry.devilry_import_v2database.modelimporters.modelimporter_utils import BulkCreator


class FeedbackSetImporter(modelimporter.ModelImporter):
    def get_model_class(self):
        return FeedbackSet

    def _create_feedback_set_from_object_dict(self, object_dict):
        feedback_set = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=feedback_set,
            object_dict=object_dict,
            attributes=[
                'pk',
                ('deadline', 'deadline_datetime'),
                ('deadline', 'created_datetime'),
            ]
        )
        feedback_set.group_id = object_dict['fields']['assignment_group']
        feedback_set.feedbackset_type = FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT  #self._get_feedback_set_type(assignment_group=assignment_group)
        if self.should_clean():
            feedback_set.full_clean()
        return feedback_set

    def import_models(self, fake=False):
        directory_parser = self.v2deadline_directoryparser
        directory_parser.set_max_id_for_models_with_auto_generated_sequence_numbers(model_class=self.get_model_class())
        with BulkCreator(model_class=FeedbackSet) as feedbackset_bulk_creator:
            for object_dict in directory_parser.iterate_object_dicts():
                if fake:
                    print('Would import: {}'.format(pprint.pformat(object_dict)))
                else:
                    feedback_set = self._create_feedback_set_from_object_dict(object_dict=object_dict)
                    feedbackset_bulk_creator.add(feedback_set)
