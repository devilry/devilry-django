import unittest

from django import test
from django.utils import timezone
from model_bakery import baker

from devilry.devilry_group.models import FeedbackSet
from devilry.devilry_import_v2database.modelimporters.feedbackset_importer import FeedbackSetImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


@unittest.skip('Not relevant anymore, keep for history.')
class TestFeedbackSetImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_model_meta(self):
        return {
            'model_class_name': 'Deadline',
            'max_id': 156,
            'app_label': 'core'
        }

    def _create_deadline_dict(self, assignment_group):
        return {
            'pk': 13,
            'model': 'core.deadline',
            'fields': {
                'feedbacks_published': True,
                'deliveries_available_before_deadline': False,
                'text': None,
                'deadline': '2016-04-11T11:04:00',
                'assignment_group': assignment_group.id,
                'why_created': None,
                'added_by': None}
        }

    def test_importer(self):
        test_group = baker.make('core.AssignmentGroup')
        self.create_v2dump(
            model_name='core.deadline',
            data=self._create_deadline_dict(assignment_group=test_group)
        )
        feedback_set_importer = FeedbackSetImporter(input_root=self.temp_root_dir)
        feedback_set_importer.import_models()
        self.assertEqual(FeedbackSet.objects.count(), 1)

    def test_importer_feedback_sets_multiple(self):
        test_group = baker.make('core.AssignmentGroup',
                                parentnode__publishing_time=timezone.now() - timezone.timedelta(days=10))
        feedback_set_data_dict = self._create_deadline_dict(assignment_group=test_group)

        # First FeedbackSet
        feedback_set_data_dict['pk'] = 1
        self.create_v2dump(model_name='core.deadline', data=feedback_set_data_dict)
        FeedbackSetImporter(input_root=self.temp_root_dir).import_models()
        feedback_set_data_dict = self._create_deadline_dict(assignment_group=test_group)

        # Second FeedbackSet
        feedback_set_data_dict['pk'] = 2
        self.create_v2dump(model_name='core.deadline', data=feedback_set_data_dict)
        FeedbackSetImporter(input_root=self.temp_root_dir).import_models()

        # Third FeedbackSet
        feedback_set_data_dict = self._create_deadline_dict(assignment_group=test_group)
        feedback_set_data_dict['pk'] = 3
        self.create_v2dump(model_name='core.deadline', data=feedback_set_data_dict)
        FeedbackSetImporter(input_root=self.temp_root_dir).import_models()

        feedback_sets = FeedbackSet.objects.filter(group=test_group).order_by('created_datetime')
        feedbackset1 = feedback_sets[0]
        feedbackset2 = feedback_sets[1]
        feedbackset3 = feedback_sets[2]

        self.assertEqual(feedbackset1.id, 1)
        self.assertEqual(feedbackset1.feedbackset_type, FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT)
        self.assertEqual(feedbackset1.created_datetime, feedbackset1.deadline_datetime)

        self.assertEqual(feedbackset2.id, 2)
        self.assertEqual(feedbackset2.feedbackset_type, FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT)
        self.assertEqual(feedbackset2.created_datetime, feedbackset2.deadline_datetime)

        self.assertEqual(feedbackset3.id, 3)
        self.assertEqual(feedbackset3.feedbackset_type, FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT)
        self.assertEqual(feedbackset3.created_datetime, feedbackset3.deadline_datetime)

    def test_auto_sequence_numbered_objects_uses_meta_max_id(self):
        test_group = baker.make('core.AssignmentGroup')
        self.create_v2dump(
            model_name='core.deadline',
            data=self._create_deadline_dict(assignment_group=test_group),
            model_meta=self._create_model_meta()
        )
        feedback_set_importer = FeedbackSetImporter(input_root=self.temp_root_dir)
        feedback_set_importer.import_models()
        self.assertEqual(FeedbackSet.objects.count(), 1)
        feedback_set = FeedbackSet.objects.first()
        self.assertEqual(feedback_set.pk, 13)
        self.assertEqual(feedback_set.id, 13)
        feedback_set_with_auto_id = baker.make('devilry_group.FeedbackSet')
        self.assertEqual(feedback_set_with_auto_id.pk, self._create_model_meta()['max_id']+1)
        self.assertEqual(feedback_set_with_auto_id.id, self._create_model_meta()['max_id']+1)
