from django.utils.translation import ugettext_lazy
from rest_framework.exceptions import PermissionDenied


from devilry.devilry_api.assignment.serializers.serializer_base import BaseAssignmentSerializer
from devilry.apps.core.models import Period, Assignment
from devilry.devilry_account.models import PeriodPermissionGroup

class PeriodAdminAssignmentSerializer(BaseAssignmentSerializer):
    """
    Period admin assignment serializer
    """
    class Meta(BaseAssignmentSerializer.Meta):
        read_only_fields = ('anonymizationmode', 'id')
        fields = BaseAssignmentSerializer.Meta.fields + [
            'students_can_see_points',
            'delivery_types',
            'deadline_handling',
            'scale_points_percent',
            'first_deadline',
            'max_points',
            'passing_grade_min_points',
            'grading_system_plugin_id',
            'points_to_grade_mapper',
            'students_can_create_groups',
            'students_can_not_create_groups_after',
            'feedback_workflow',
        ]

    def validate(self, data):
        """
        pop period id to parentnode
        Args:
            data: dictionary

        Returns:
            dictionary with validated data

        """
        data['parentnode'] = data.pop('period_id')
        return data

    def validate_period_id(self, value):
        """
        Validate period id check that period admin is part of period.
        and return Period
        Args:
            value: :attr:`~apps.core.Period.id`

        Returns:
            :obj:`~apps.core.Period`
        """
        try:
            return Period.objects.filter_user_is_period_admin(self.context['request'].user).get(id=value)
        except Period.DoesNotExist:
            raise PermissionDenied(ugettext_lazy('Access denied Period admin not part of period.'))

    def create(self, validated_data):
        """
        Creates a new assignment
        Args:
            validated_data: dictionary with validated data

        Returns:
            :obj:`~apps.core.Assignment`
        """
        return Assignment.objects.create(anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF,
                                         **validated_data)
