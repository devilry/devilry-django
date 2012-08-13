from django.db.models import Q
from djangorestframework.views import ModelView
from djangorestframework.mixins import InstanceMixin
from djangorestframework.mixins import ReadModelMixin
from djangorestframework.resources import ModelResource
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.permissions import BasePermission
from djangorestframework.response import ErrorResponse
from djangorestframework import status


from devilry.apps.core.models import AssignmentGroup


class IsCandidate(BasePermission):
    """
    Djangorestframework permission checker that checks if the requesting user
    is candidate on the requested group.
    """
    def check_permission(self, user):
        groupid = self.view.kwargs['id']
        try:
            AssignmentGroup.where_is_candidate(user).get(id=groupid)
        except AssignmentGroup.DoesNotExist, e:
            raise ErrorResponse(status.HTTP_403_FORBIDDEN,
                                {'detail': 'Only candidates on group with ID={0} can make this request.'.format(groupid)})

class GroupResource(ModelResource):
    fields = ('id', 'name', 'is_open', 'candidates', 'deadlines')
    model = AssignmentGroup

    def format_user(self, user):
        return {'email': user.email,
                'username': user.username,
                'id': user.id,
                'full_name': user.devilryuserprofile.full_name}

    def format_candidate(self, candidate):
        cand = {'id': candidate.id,
                'user': self.format_user(candidate.student),
                'candidate_id': candidate.candidate_id,
                'identifier': candidate.identifier}
        return cand

    def candidates(self, instance):
        return map(self.format_candidate, instance.candidates.all())


    def format_timedelta(self, td):
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return {'days': abs(td.days),
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds}

    def format_feedback(self, staticfeedback):
        return {'id': staticfeedback.id,
                'save_timestamp': staticfeedback.save_timestamp,
                'grade': staticfeedback.grade,
                # NOTE: points is not included because students are not supposed to get direct access to points.
                'is_passing_grade': staticfeedback.is_passing_grade}

    def format_filemeta(self, filemeta):
        return {'id': filemeta.id,
                'filename': filemeta.filename,
                'size': filemeta.size}

    def format_delivery(self, delivery):
        timedelta_before_deadline = delivery.deadline.deadline - delivery.time_of_delivery
        return {'id': delivery.id,
                'number': delivery.number,
                'delivered_by': self.format_candidate(delivery.delivered_by),
                'after_deadline': delivery.after_deadline,
                'time_of_delivery': delivery.time_of_delivery,
                'offset_from_deadline': self.format_timedelta(timedelta_before_deadline),
                'alias_delivery': delivery.alias_delivery_id,
                'feedbacks': map(self.format_feedback, delivery.feedbacks.all()),
                'filemetas': map(self.format_filemeta, delivery.filemetas.all())}

    def format_deliveries(self, deadline):
        return map(self.format_delivery, deadline.deliveries.filter(successful=True))

    def format_deadline(self, deadline):
        return {'id': deadline.id,
                'deadline': deadline.deadline,
                'text': deadline.text,
                'deliveries': self.format_deliveries(deadline)}

    def deadlines(self, instance):
        return map(self.format_deadline, instance.deadlines.all())


class AggregatedGroupInfo(InstanceMixin, ReadModelMixin, ModelView):
    """
    Provides an API that aggregates a lot of information about a group.

    # GET
    An object with the following attributes:

    - ``id`` (int): Internal Devilry ID of the group. Is never ``null``.
    """
    permissions = (IsAuthenticated, IsCandidate)
    resource = GroupResource

    def get_queryset(self):
        qry = super(AggregatedGroupInfo, self).get_queryset()
        return qry
