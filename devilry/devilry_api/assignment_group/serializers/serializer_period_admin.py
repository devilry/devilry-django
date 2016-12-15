from devilry.apps.core.models import AssignmentGroup
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
