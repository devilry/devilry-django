from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
import numpy

from devilry_subjectadmin.rest.auth import IsAssignmentAdmin
from devilry.apps.core.models import Assignment
from devilry.utils.restformat import serialize_user
from .group import GroupSerializer


class SingleExaminerStats(object):
    STATUS_TO_ATTR_MAP = {
        'waiting-for-deliveries': 'waitingfordeliveries_count',
        'waiting-for-feedback': 'waitingforfeedback_count',
        'no-deadlines': 'nodeadlines_count',
        'corrected': 'corrected_count',
        'closed-without-feedback': 'closedwithoutfeedback_count',
        }
    def __init__(self, examiner):
        self.examiner = examiner
        self.waitingfordeliveries = []
        self.waitingforfeedback = []
        self.nodeadlines = []
        self.closedwithoutfeedback = []
        self.failed = []
        self.passed = []
        self.allgroups = []

    def _serialize_group(self, group):
        serializer = GroupSerializer(group)
        return {
            'id': group.id,
            'candidates': serializer.serialize_candidates()
        }

    def _serialize_groups(self, groups):
        return map(self._serialize_group, groups)

    def add_group(self, group):
        self.allgroups.append(group)


    def aggregate_data(self):
        self.points_best = None
        self.points_worst = None
        allpoints = []
        for group in self.allgroups:
            status = group.get_status()
            if status == 'corrected':
                feedback = group.feedback
                points = feedback.points
                if group.feedback.is_passing_grade:
                    self.passed.append(group)
                else:
                    self.failed.append(group)
                if self.points_best == None or points > self.points_best:
                    self.points_best = points
                if self.points_worst == None or points < self.points_worst:
                    self.points_worst = points
                allpoints.append(points) # We only collect corrected -- avg is average of corrected
            else:
                attrname = self.STATUS_TO_ATTR_MAP[status]
                value = getattr(self, attrname)
                setattr(self, attrname, value + 1)
        self.points_avg = numpy.mean(allpoints)


    def serialize(self):
        return {
            'id': self.examiner.user_id,
            'examiner': {
                'id': self.examiner.id,
                'user': serialize_user(self.examiner.user)
            },
            'waitingfordeliveries_count': self.waitingfordeliveries_count,
            'waitingforfeedback_count': self.waitingforfeedback_count,
            'nodeadlines_count': self.nodeadlines_count,
            'closedwithoutfeedback_count': self.closedwithoutfeedback_count,
            'failed_count': self.failed_count,
            'passed_count': self.passed_count,
            'groups': self._serialize_groups(self.allgroups),
            'points_best': self.points_best,
            'points_worst': self.points_worst,
            'points_avg': self.points_avg
        }


class AggregatedExaminerStats(object):
    def __init__(self):
        self.examiners = {}

    def add_examiner(self, examiner, group):
        if not examiner.user_id in self.examiners:
            self.examiners[examiner.user_id] = SingleExaminerStats(examiner)
        self.examiners[examiner.user_id].add_group(group)

    def aggregate_data(self):
        for examiner in self.examiners.itervalues():
            examiner.aggregate_data()

    def serialize(self):
        self.aggregate_data()
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
            for examiner in group.examiners.all():
                examiners.add_examiner(examiner, group)
        return examiners

    def get(self, request, id=None):
        # NOTE: We know the assignment exists because of IsAssignmentAdmin
        self.assignment = Assignment.objects.get(id=id)
        return self._group_by_examiner().serialize()