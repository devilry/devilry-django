from devilry.devilry_api.assignment_group.serializers import serializer_base
from devilry.apps.core.models import AssignmentGroup


class CandidateSerializer(serializer_base.AbstractCandidateSerializer):
    """
    Candidate in assignment group shown as student role.
    """
    devilry_role = 'student'


class ExaminerSerializer(serializer_base.AbstractExaminerSerializer):
    """
    Examiner in assignment group shown as student role.
    """
    devilry_role = 'student'


class AssignmentGroupModelSerializer(serializer_base.AbstractAssignmentGroupSerializer):
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

