from django import test
from django.core.exceptions import ValidationError

from model_mommy import mommy

from devilry.devilry_merge_v3database.models import TempMergeId
from devilry.devilry_group import models as group_models


class TestTempMergeId(test.TestCase):
    def test_manager_create(self):
        feedback_set1 = mommy.make('devilry_group.FeedbackSet', id=10)
        feedback_set2 = mommy.make('devilry_group.FeedbackSet', id=250)
        temp_merge_id = TempMergeId.objects.create_from_instances(
            merge_to_obj=feedback_set1,
            merge_from_obj=feedback_set2
        )
        self.assertEqual(temp_merge_id.to_id, 10)
        self.assertEqual(temp_merge_id.from_id, 250)
        self.assertEqual(temp_merge_id.model_name, 'devilry_group_feedbackset')

    def test_manager_create_raises_validation_error_different_classes(self):
        feedback_set = mommy.make('devilry_group.FeedbackSet', id=10)
        group_comment = mommy.make('devilry_group.GroupComment', id=250)
        with self.assertRaisesMessage(
                ValidationError,
                'Must be models of same type: devilry_group_feedbackset != devilry_group_groupcomment'):
            TempMergeId.objects.create_from_instances(
                merge_to_obj=feedback_set,
                merge_from_obj=group_comment
            )
        with self.assertRaisesMessage(
                ValidationError,
                'Must be models of same type: devilry_group_groupcomment != devilry_group_feedbackset'):
            TempMergeId.objects.create_from_instances(
                merge_to_obj=group_comment,
                merge_from_obj=feedback_set
            )


