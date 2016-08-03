from devilry.devilry_api.assignment_group.serializers import serializer_base
from devilry.apps.core.models import AssignmentGroup


class CandidateSerializer(serializer_base.CandidateSerializer):
    """
    Candidate in assignment group shown as student role.
    """
    devilry_role = 'student'


class ExaminerSerializer(serializer_base.ExaminerSerializer):
    """
    Examiner in assignment group shown as student role.
    """
    devilry_role = 'student'


class AssignmentGroupModelSerializer(serializer_base.AssignmentGroupModelSerializer):
    #: Candidates in assignment group
    candidates = CandidateSerializer(many=True)

    #: Examiners in assignment group
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

