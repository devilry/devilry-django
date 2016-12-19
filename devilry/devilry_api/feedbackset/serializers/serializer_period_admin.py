from rest_framework import serializers
from django.utils.translation import ugettext_lazy

from devilry.devilry_api.feedbackset.serializers.serializer_examiner import FeedbacksetSerializerExaminer
from devilry.apps.core.models import AssignmentGroup


class FeedbacksetSerializerPeriodAadmin(FeedbacksetSerializerExaminer):
    devilry_role = 'periodadmin'

    def validate_group_id(self, value):
        """
        Makes sure that period admin has access to assignment group

        Args:
            value: :attr:`~core.AssignmentGroup.id`

        Returns:
            :attr:`~core.AssignemntGroup.id`
        """
        try:
            AssignmentGroup.objects \
                .filter_user_is_period_admin(user=self.context['request'].user) \
                .get(id=value)
        except AssignmentGroup.DoesNotExist:
            raise serializers.ValidationError(ugettext_lazy('Access denied ' 'Period admin not part of period'))
        return value
