import pprint

from django.utils import timezone

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_import_v2database import modelimporter


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

    def _get_feedback_set_type(self, assignment_group):
        """
        Checking imported models if a FeedbackSet has already been added.
        """
        if assignment_group.feedbackset_set.count() == 0:
            return FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT
        return FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT

    def _get_created_datetime(self, assignment_group):
        """
        Get what should be the created_datetime for a ``FeedbackSet``.

        Notes::
            We need do this as the ``Deadline`` from V2 has no information on when it was created.

        Returns:
            datetime (DateTime): If the AssignmentGroup has no FeedbackSets,
                Assignment.publishing_time is returned.
                If the AssignmentGroup has one or more FeedbackSets, the created_datetime of the
                last FeedbackSet + 1 hour is returned.
        """
        feedbackset_queryset = FeedbackSet.objects.filter(group=assignment_group).order_by('created_datetime')
        if feedbackset_queryset.count() == 0:
            return assignment_group.parentnode.publishing_time
        last_feedbackset = feedbackset_queryset.last()
        return last_feedbackset.created_datetime + timezone.timedelta(hours=1)

    def _create_feedback_set_from_object_dict(self, object_dict):
        feedback_set = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=feedback_set,
            object_dict=object_dict,
            attributes=[
                'pk',
                ('deadline', 'deadline_datetime')
            ]
        )
        assignment_group = self._get_assignment_group_from_id(
            assignment_group_id=object_dict['fields']['assignment_group'])
        feedback_set.group = assignment_group
        feedback_set.feedbackset_type = self._get_feedback_set_type(assignment_group=assignment_group)
        feedback_set.created_datetime = self._get_created_datetime(assignment_group=assignment_group)
        feedback_set.full_clean()
        feedback_set.save()
        self.log_create(model_object=feedback_set, data=object_dict)

    def import_models(self, fake=False):
        directory_parser = self.v2deadline_directoryparser
        directory_parser.set_max_id_for_models_with_auto_generated_sequence_numbers(model_class=self.get_model_class())
        for object_dict in directory_parser.iterate_object_dicts():
            if fake:
                print('Would import: {}'.format(pprint.pformat(object_dict)))
            else:
                self._create_feedback_set_from_object_dict(object_dict=object_dict)
