import unittest

from django import test
from django.conf import settings

from model_bakery import baker

from devilry.devilry_group.models import FeedbackSet, GroupComment
from devilry.devilry_import_v2database.modelimporters.delivery_feedback_importers import DeliveryImporter
from .importer_testcase_mixin import ImporterTestCaseMixin


@unittest.skip('Not relevant anymore, keep for history.')
class TestDeliveryImporterImporter(ImporterTestCaseMixin, test.TestCase):
    def _create_model_meta(self):
        return {
            'model_class_name': 'Delivery',
            'max_id': 143,
            'app_label': 'core'
        }

    def _create_delivery_dict(self, feedback_set, candidate_id=None):
        return {
            'pk': 3,
            'model': 'core.delivery',
            'fields': {
                'delivery_type': 0,
                'alias_delivery': None,
                'successful': True,
                'number': 1,
                'delivered_by': candidate_id,
                'last_feedback': 3,
                'deadline': feedback_set.id,
                'copy_of': None,
                'time_of_delivery': '2016-04-10T07:04:00'
            },
        }

    def test_importer(self):
        test_student_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        candidate = baker.make('core.Candidate',
                               assignment_group=test_group,
                               relatedstudent__user=test_student_user,
                               relatedstudent__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.delivery',
            data=self._create_delivery_dict(
                feedback_set=test_feedbackset,
                candidate_id=candidate.id),
        )
        DeliveryImporter(input_root=self.temp_root_dir).import_models()
        self.assertEqual(FeedbackSet.objects.count(), 1)
        self.assertEqual(GroupComment.objects.count(), 1)

    def test_importer_pk(self):
        test_student_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        candidate = baker.make('core.Candidate',
                               assignment_group=test_group,
                               relatedstudent__user=test_student_user,
                               relatedstudent__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.delivery',
            data=self._create_delivery_dict(
                feedback_set=test_feedbackset,
                candidate_id=candidate.id)
        )
        DeliveryImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertEqual(comment.pk, 3)
        self.assertEqual(comment.id, 3)

    def test_importer_feedback_set(self):
        test_student_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        candidate = baker.make('core.Candidate',
                               assignment_group=test_group,
                               relatedstudent__user=test_student_user,
                               relatedstudent__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.delivery',
            data=self._create_delivery_dict(
                feedback_set=test_feedbackset,
                candidate_id=candidate.id)
        )
        DeliveryImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertEqual(comment.feedback_set, test_feedbackset)

    def test_importer_text(self):
        test_student_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        candidate = baker.make('core.Candidate',
                               assignment_group=test_group,
                               relatedstudent__user=test_student_user,
                               relatedstudent__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.delivery',
            data=self._create_delivery_dict(
                feedback_set=test_feedbackset,
                candidate_id=candidate.id)
        )
        DeliveryImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertEqual(comment.text, 'Delivery')

    def test_importer_comment_type(self):
        test_student_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        candidate = baker.make('core.Candidate',
                               assignment_group=test_group,
                               relatedstudent__user=test_student_user,
                               relatedstudent__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.delivery',
            data=self._create_delivery_dict(
                feedback_set=test_feedbackset,
                candidate_id=candidate.id)
        )
        DeliveryImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertEqual(comment.comment_type, GroupComment.COMMENT_TYPE_GROUPCOMMENT)

    def test_importer_comment_part_of_grading_false(self):
        test_student_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        candidate = baker.make('core.Candidate',
                               assignment_group=test_group,
                               relatedstudent__user=test_student_user,
                               relatedstudent__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.delivery',
            data=self._create_delivery_dict(
                feedback_set=test_feedbackset,
                candidate_id=candidate.id)
        )
        DeliveryImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertFalse(comment.part_of_grading)

    def test_importer_user(self):
        test_student_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        candidate = baker.make('core.Candidate',
                               assignment_group=test_group,
                               relatedstudent__user=test_student_user,
                               relatedstudent__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.delivery',
            data=self._create_delivery_dict(
                feedback_set=test_feedbackset,
                candidate_id=candidate.id)
        )
        DeliveryImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertEqual(comment.user, test_student_user)

    def test_importer_user_role(self):
        test_student_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        candidate = baker.make('core.Candidate',
                               assignment_group=test_group,
                               relatedstudent__user=test_student_user,
                               relatedstudent__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.delivery',
            data=self._create_delivery_dict(
                feedback_set=test_feedbackset,
                candidate_id=candidate.id)
        )
        DeliveryImporter(input_root=self.temp_root_dir).import_models()
        comment = GroupComment.objects.first()
        self.assertEqual(comment.user_role, GroupComment.USER_ROLE_STUDENT)

    def test_auto_sequence_numbered_objects_uses_meta_max_id(self):
        test_student_user = baker.make(settings.AUTH_USER_MODEL)
        test_group = baker.make('core.AssignmentGroup')
        candidate = baker.make('core.Candidate',
                               assignment_group=test_group,
                               relatedstudent__user=test_student_user,
                               relatedstudent__period=test_group.parentnode.parentnode)
        test_feedbackset = baker.make('devilry_group.FeedbackSet', group=test_group)
        self.create_v2dump(
            model_name='core.delivery',
            data=self._create_delivery_dict(
                feedback_set=test_feedbackset,
                candidate_id=candidate.id),
            model_meta=self._create_model_meta()
        )
        DeliveryImporter(input_root=self.temp_root_dir).import_models()
        self.assertEqual(GroupComment.objects.count(), 1)
        comment = GroupComment.objects.first()
        self.assertEqual(comment.pk, 3)
        self.assertEqual(comment.id, 3)
        comment_with_auto_id = baker.make('devilry_group.GroupComment')
        self.assertEqual(comment_with_auto_id.pk, self._create_model_meta()['max_id']+1)
        self.assertEqual(comment_with_auto_id.id, self._create_model_meta()['max_id']+1)
