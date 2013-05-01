from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from django.conf import settings

from devilry.apps.core.models import AssignmentGroup
from devilry.utils import OrderedDict
from devilry_qualifiesforexam.models import QualifiesForFinalExam
from devilry_qualifiesforexam.models import Status



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
    def __init__(self, qryset, devilry_qualifiesforexam_enabled, user):
        self.qry = qryset
        self.devilry_qualifiesforexam_enabled = devilry_qualifiesforexam_enabled
        self.user = user

    def _serialize_subject(self, subject):
        return {
                'id': subject.id,
                'short_name': subject.short_name,
                'long_name': subject.long_name,
                'periods': OrderedDict()
        }

    def _serialize_period(self, period):
        out = {
                'id': period.id,
                'short_name': period.short_name,
                'long_name': period.long_name,
                'assignments': OrderedDict(),
                'is_relatedstudent': period.relatedstudent_set.filter(user=self.user).exists()
        }
        if self.devilry_qualifiesforexam_enabled:
            out['qualifiesforexams'] = None
            try:
                status = Status.get_current_status(period)
            except Status.DoesNotExist:
                pass
            else:
                if status.status == Status.READY:
                    try:
                        qualifies = status.students.get(relatedstudent__user=self.user)
                        out['qualifiesforexams'] = qualifies.qualifies
                    except QualifiesForFinalExam.DoesNotExist:
                        pass
        return out

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
                '-parentnode__parentnode__start_time',
                '-parentnode__publishing_time', 'parentnode__short_name'):
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
        devilry_qualifiesforexam_enabled = 'devilry_qualifiesforexam' in settings.INSTALLED_APPS
        if self.request.GET.get('activeonly', False) == 'true':
            qry = AssignmentGroup.active_where_is_candidate(self.request.user)
        else:
            qry = AssignmentGroup.published_where_is_candidate(self.request.user)
        return GroupedBySubjectSerialize(qry, devilry_qualifiesforexam_enabled, request.user).serialize()
