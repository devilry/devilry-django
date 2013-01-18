from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated

from devilry_subjectadmin.rest.auth import IsAssignmentAdmin
from devilry.apps.core.models import Assignment
from devilry.utils.restformat import serialize_user
from .group import GroupSerializer


class SingleExaminerStats(object):
    STATUS_TO_ATTR_MAP = {
        'waiting-for-deliveries': 'waitingfordeliveries',
        'waiting-for-feedback': 'waitingforfeedback',
        'no-deadlines': 'nodeadlines',
        'corrected': 'corrected',
        'closed-without-feedback': 'closedwithoutfeedback',
        }
    def __init__(self, examiner):
        self.examiner = examiner
        self.waitingfordeliveries = []
        self.waitingforfeedback = []
        self.nodeadlines = []
        self.corrected = []
        self.closedwithoutfeedback = []

    def _serialize_group(self, group):
        serializer = GroupSerializer(group)
        return {
            'id': group.id,
            'candidates': serializer.serialize_candidates()
        }

    def _serialize_groups(self, groups):
        return map(self._serialize_group, groups)

    def add_group(self, group, status):
        attrname = self.STATUS_TO_ATTR_MAP[status]
        getattr(self, attrname).append(group)

    def serialize(self):
        return {
            'id': self.examiner.user_id,
            'examiner': {
                'id': self.examiner.id,
                'user': serialize_user(self.examiner.user)
            },
            'waitingfordeliveries': self._serialize_groups(self.waitingfordeliveries),
            'waitingforfeedback': self._serialize_groups(self.waitingforfeedback),
            'nodeadlines': self._serialize_groups(self.nodeadlines),
            'corrected': self._serialize_groups(self.corrected),
            'closedwithoutfeedback': self._serialize_groups(self.closedwithoutfeedback)
        }



class AggregatedExaminerStats(object):
    def __init__(self):
        self.examiners = {}

    def add_examiner(self, examiner, group, status):
        if not examiner.user_id in self.examiners:
            self.examiners[examiner.user_id] = SingleExaminerStats(examiner)
        self.examiners[examiner.user_id].add_group(group, status)

    def serialize(self):
        return [examiner.serialize() for examiner in self.examiners.itervalues()]


class ExaminerStats(View):
    """
    Statistics for all examiners on an assignment.

    # GET

    ## Parameters
    Takes the assignment ID as the last item in the URL-path.

    ## Returns
    """
    permissions = (IsAuthenticated, IsAssignmentAdmin)

    def _groupqry(self):
        qry = self.assignment.assignmentgroups.all()
        qry = qry.prefetch_related(
            'deadlines',
            'tags',
            'examiners', 'examiners__user',
            'examiners__user__devilryuserprofile',
            'feedback',
            'candidates', 'candidates__student',
            'candidates__student__devilryuserprofile')
        return qry

    def _group_by_examiner(self):
        groups = self._groupqry()
        examiners = AggregatedExaminerStats()
        for group in groups.all():
            status = group.get_status()
            for examiner in group.examiners.all():
                examiners.add_examiner(examiner, group, status)
        return examiners

    def get(self, request, id=None):
        # NOTE: We know the assignment exists because of IsAssignmentAdmin
        self.assignment = Assignment.objects.get(id=id)
        return self._group_by_examiner().serialize()