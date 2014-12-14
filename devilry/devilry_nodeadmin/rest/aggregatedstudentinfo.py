from simple_rest import Resource
from simple_rest.response import RESTfulResponse
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User

from devilry.devilry_rest.auth import authentication_required
from devilry.devilry_rest.serializehelpers import format_datetime
from devilry.devilry_rest.serializehelpers import serialize_user
from devilry.apps.core.models import Node
from devilry.apps.core.models import Candidate
from devilry.devilry_qualifiesforexam.models import QualifiesForFinalExam
from devilry.devilry_qualifiesforexam.models import Status


class MappedList(list):
    """
    A ordered-dict-like object that serializes to a list.
    """
    def __init__(self):
        self._itemsdict = {}

    def __getitem__(self, key):
        return self._itemsdict[key]

    def __setitem__(self, key, value):
        if key in self._itemsdict:
            raise ValueError('key {} already in the list'.format(key))
        self._itemsdict[key] = value
        super(MappedList, self).append(value)

    def __contains__(self, key):
        return key in self._itemsdict

    def append(self, value):
        raise NotImplementedError()


@authentication_required
class AggregatedStudentInfo(Resource):

    def _serialize_subject(self, subject):
        return {
            'id': subject.id,
            'short_name': subject.short_name,
            'long_name': subject.long_name,
            'periods': MappedList()
        }

    def _serialize_period(self, period, userobj, devilry_qualifiesforexam_enabled):
        qualifies = None

        if devilry_qualifiesforexam_enabled:
            try:
                status = Status.get_current_status(period)
            except Status.DoesNotExist:
                pass
            else:
                if status.status == Status.READY:
                    try:
                        qualification_status = status.students.get(relatedstudent__user=userobj)
                        qualifies = qualification_status.qualifies
                    except QualifiesForFinalExam.DoesNotExist:
                        pass

        return {
            'id': period.id,
            'short_name': period.short_name,
            'long_name': period.long_name,
            'start_time': format_datetime(period.start_time),
            'end_time': format_datetime(period.end_time),
            'is_active': period.is_active(),
            'is_relatedstudent': period.relatedstudent_set.filter(user=userobj).exists(),
            'qualified_forexams': qualifies,
            'assignments': MappedList()
        }

    def _serialize_assignment(self, assignment):
        return {
            'id': assignment.id,
            'short_name': assignment.short_name,
            'long_name': assignment.long_name,
            'publishing_time': format_datetime(assignment.publishing_time),
            'deadline_handling': assignment.deadline_handling,
            'anonymous': assignment.anonymous,
            'delivery_types': assignment.delivery_types,
            'groups': []
        }

    def _serialize_feedback(self, staticfeedback):
        return {'id': staticfeedback.id,
                'rendered_view': staticfeedback.rendered_view,
                'save_timestamp': format_datetime(staticfeedback.save_timestamp),
                'grade': staticfeedback.grade,
                'is_passing_grade': staticfeedback.is_passing_grade}

    def _serialize_active_feedback(self, group):
        if group.feedback:
            feedback = group.feedback
            return {'feedback': self._serialize_feedback(feedback),
                    'deadline_id': feedback.delivery.deadline_id,
                    'delivery_id': feedback.delivery_id}
        else:
            return None

    def _serialize_group(self, group):
        return {
            'id': group.id,
            'status': group.get_status(),
            'active_feedback': self._serialize_active_feedback(group)
        }

    def _group_candidates_by_hierarky(self, candidates, userobj, devilry_qualifiesforexam_enabled):
        grouped_by_subject = MappedList()
        for candidate in candidates:
            group = candidate.assignment_group
            assignment = group.parentnode
            period = assignment.parentnode
            subject = period.parentnode

            if not subject.short_name in grouped_by_subject:
                #grouped_by_subject['] = self._serialize_subject(subject)
                grouped_by_subject[subject.short_name] = self._serialize_subject(subject)

            periodsdict = grouped_by_subject[subject.short_name]['periods']
            if not period.short_name in periodsdict:
                periodsdict[period.short_name] = self._serialize_period(period, userobj, devilry_qualifiesforexam_enabled)

            assignmentsdict = periodsdict[period.short_name]['assignments']
            if not assignment.short_name in assignmentsdict:
                assignmentsdict[assignment.short_name] = self._serialize_assignment(assignment)

            # NOTE: A candidate can not be multiple times in one group, so no
            #       need for the IF and dict used on the other levels of the
            #       hierarchy.
            groups = assignmentsdict[assignment.short_name]['groups']
            groups.append(self._serialize_group(group))

        return grouped_by_subject

    @RESTfulResponse()
    def get(self, request, user_id, **kwargs):
        # # Hack to force json return.
        # request.META['HTTP_ACCEPT'] = 'application/json'
        try:
            userobj = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None, 404
        devilry_qualifiesforexam_enabled = 'devilry_qualifiesforexam' in settings.INSTALLED_APPS
        adminuserobj = self.request.user
        candidates = Candidate.objects.filter(student=userobj)
        if not adminuserobj.is_superuser:
            nodepks_where_is_admin = Node._get_nodepks_where_isadmin(adminuserobj)
            candidates = candidates.filter(
                    Q(assignment_group__parentnode__admins=adminuserobj) | \
                    Q(assignment_group__parentnode__parentnode__admins=adminuserobj) | \
                    Q(assignment_group__parentnode__parentnode__parentnode__admins=adminuserobj) | \
                    Q(assignment_group__parentnode__parentnode__parentnode__parentnode__pk__in=nodepks_where_is_admin))
        candidates = candidates.order_by(
                'assignment_group__parentnode__parentnode__parentnode__short_name',
                '-assignment_group__parentnode__parentnode__start_time',
                'assignment_group__parentnode__publishing_time',
                'assignment_group__parentnode__short_name',
                )
        return {
            'user': serialize_user(userobj),
            'grouped_by_hierarky': self._group_candidates_by_hierarky(candidates, userobj, devilry_qualifiesforexam_enabled),
        }
