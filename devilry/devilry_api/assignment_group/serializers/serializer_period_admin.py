from django.utils.translation import ugettext_lazy
from rest_framework.exceptions import PermissionDenied


from devilry.apps.core.models import AssignmentGroup, Assignment
from devilry.devilry_api.assignment_group.serializers import serializer_base


class CandidateSerializer(serializer_base.BaseCandidateSerializer):
    """
    Candidate in assignment group shown as examiner role.
    """
    devilry_role = 'periodadmin'


class ExaminerSerializer(serializer_base.BaseExaminerSerializer):
    """
    Examiner in assignment group shown as examiner role.
    """
    devilry_role = 'periodadmin'


class AssignmentGroupModelSerializer(serializer_base.BaseAssignmentGroupSerializer):
    #: Candidates in assignment group
    candidates = CandidateSerializer(many=True, required=False)

    #: Examiners in assignment group
    examiners = ExaminerSerializer(many=True, required=False)

    class Meta:
        read_only_fields = ('candidates',
                            'examiners',
                            'is_waiting_for_feedback',
                            'is_waiting_for_deliveries',
                            'is_corrected',)
        model = AssignmentGroup
        fields = [
            'id',
            'name',
            'assignment_id',
            'assignment_short_name',
            'subject_short_name',
            'period_short_name',
            'short_displayname',
            'long_displayname',
            'is_waiting_for_feedback',
            'is_waiting_for_deliveries',
            'is_corrected',
            'candidates',
            'examiners',
        ]

    def validate(self, data):
        """
        Checks that request user is period admin for assignment

        Args:
            data: request data

        Raises:
            :class:`rest_framework.exceptions.PermissionDenied`

        Returns:
            dictionary with validated data
        """
        validated_data = dict()
        validated_data['parentnode'] = Assignment.objects \
            .filter_user_is_period_admin(self.context['request'].user) \
            .filter(id=data.pop('assignment_id')).first()
        if validated_data['parentnode'] is None:
            raise PermissionDenied(ugettext_lazy('Permission denied: not part of period'))
        validated_data['name'] = data['name']
        return validated_data

    def create(self, validated_data):
        """
        Creates a new Assignment group

        Args:
            validated_data: validated data

        Returns:
            :obj:`devilry_group.AssignmentGroup`
        """
        return AssignmentGroup.objects.create(**validated_data)