from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_api.assignment_group.serializers import serializer_base


class CandidateSerializer(serializer_base.CandidateSerializer):
    devilry_role = 'examiner'


class ExaminerSerializer(serializer_base.ExaminerSerializer):
    devilry_role = 'examiner'


class AssignmentGroupModelSerializer(serializer_base.AssignmentGroupModelSerializer):
    candidates = CandidateSerializer(many=True)
    examiners = ExaminerSerializer(many=True)

    class Meta:
        model = AssignmentGroup
        fields = [
            'id',
            'name',
            'assignment_id',
            'assignment_long_name',
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

