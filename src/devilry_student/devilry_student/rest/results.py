from datetime import datetime
from django.db.models import Max, Q, Count
from djangorestframework.resources import FormResource
from django import forms
from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated

from devilry.apps.core.models import AssignmentGroup
from devilry.utils import OrderedDict
from .helpers import GroupResourceHelpersMixin
from .helpers import format_datetime
from .helpers import format_timedelta
from .errors import BadRequestError



class SerializeGroupMixin(object):
    def _serialize_feedback(self, feedback):
        return {'id': feedback.id,
                'grade': feedback.grade,
                'delivery_id': feedback.delivery.id,
                'is_passing_grade': feedback.is_passing_grade,
                'save_timestamp': feedback.save_timestamp}

    def serialize_group(self, group):
        status =  group.get_status()
        feedback = None
        if status == 'corrected':
            feedback = self._serialize_feedback(group.feedback)
        return {
                'id': group.id,
                'status': status,
                'feedback': feedback
        }


class GroupedBySubjectSerialize(SerializeGroupMixin):
    def __init__(self, qryset):
        self.qry = qryset

    def _serialize_subject(self, subject):
        return {
                'id': subject.id,
                'short_name': subject.short_name,
                'long_name': subject.long_name,
                'periods': OrderedDict()
        }

    def _serialize_period(self, period):
        return {
                'id': period.id,
                'short_name': period.short_name,
                'long_name': period.long_name,
                'assignments': OrderedDict()
        }

    def _serialize_assignment(self, assignment):
        return {
                'id': assignment.id,
                'short_name': assignment.short_name,
                'long_name': assignment.long_name,
                'groups': []
        }

    def _add_or_get(self, dct, obj, serializer):
        if not obj.id in dct:
            dct[obj.id] = serializer(obj)
        return dct[obj.id]

    def serialize(self):
        subjects = OrderedDict()
        for group in self.qry.order_by(
                'parentnode__parentnode__parentnode__long_name',
                'parentnode__parentnode__start_time',
                'parentnode__publishing_time', 'parentnode__short_name'):
            subjectdict = self._add_or_get(subjects, group.subject, self._serialize_subject)
            perioddict = self._add_or_get(subjectdict['periods'], group.period, self._serialize_period)
            assignmentdict = self._add_or_get(perioddict['assignments'], group.assignment, self._serialize_assignment)
            assignmentdict['groups'].append(self.serialize_group(group))
        out = []
        for subject in subjects.itervalues():
            subject['periods'] = subject['periods'].values()
            for period in subject['periods']:
                period['assignments'] = period['assignments'].values()
        return subjects.values()



class ResultsView(View):
    """
    """
    permissions = (IsAuthenticated,)

    def get(self, request):
        if self.request.GET.get('activeonly', False) == 'true':
            qry = AssignmentGroup.active_where_is_candidate(self.request.user)
        else:
            qry = AssignmentGroup.published_where_is_candidate(self.request.user)
        return GroupedBySubjectSerialize(qry).serialize()
