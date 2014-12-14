import numpy

from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from devilry.devilry_subjectadmin.rest.auth import IsAssignmentAdmin
from devilry.apps.core.models import Assignment
from devilry.devilry_rest.serializehelpers import serialize_user
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
        self.waitingfordeliveries_count = 0
        self.waitingforfeedback_count = 0
        self.nodeadlines_count = 0
        self.closedwithoutfeedback_count = 0
        self.failed_count = 0
        self.passed_count = 0
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

    def _countwords(self, rendered_view):
        return len(rendered_view.split())

    def _percentage(self, part, whole):
        if whole == 0:
            return 0
        else:
            return 100 * float(part)/float(whole)

    def aggregate_data(self):
        self.points_best = None
        self.points_worst = None
        words = []
        allpoints = []
        for group in self.allgroups:
            status = group.get_status()
            if status == 'corrected':
                feedback = group.feedback
                points = feedback.points
                words.append(self._countwords(feedback.rendered_view))
                if group.feedback.is_passing_grade:
                    self.passed_count += 1
                else:
                    self.failed_count += 1
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
        self.feedback_words_avg = numpy.mean(words)


    def serialize(self):
        totalgroups = len(self.allgroups)
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
            'corrected_count': self.failed_count + self.passed_count,

            'waitingfordeliveries_percent': self._percentage(self.waitingfordeliveries_count, totalgroups),
            'waitingforfeedback_percent': self._percentage(self.waitingforfeedback_count, totalgroups),
            'nodeadlines_percent': self._percentage(self.nodeadlines_count, totalgroups),
            'closedwithoutfeedback_percent': self._percentage(self.closedwithoutfeedback_count, totalgroups),
            'failed_percent': self._percentage(self.failed_count, totalgroups),
            'passed_percent': self._percentage(self.passed_count, totalgroups),
            'corrected_percent': self._percentage(self.failed_count + self.passed_count, totalgroups),

            'groups': self._serialize_groups(self.allgroups),
            'points_best': self.points_best,
            'points_worst': self.points_worst,
            'points_avg': self.points_avg,
            'feedback_words_avg': self.feedback_words_avg
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
