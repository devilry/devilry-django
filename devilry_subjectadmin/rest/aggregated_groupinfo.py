from djangorestframework.views import ModelView
from djangorestframework.mixins import InstanceMixin
from djangorestframework.mixins import ReadModelMixin
from djangorestframework.permissions import IsAuthenticated

from devilry_student.rest.aggregated_groupinfo import GroupResource
from devilry.devilry_rest.serializehelpers import format_datetime
from .auth import IsGroupAdmin




class AdministratorGroupResource(GroupResource):
    fields = ('id', 'deadlines')

    def _serialize_user(self, user):
        full_name = user.devilryuserprofile.full_name
        return {'id': user.id,
                'username': user.username,
                'email': user.email,
                'displayname': full_name or user.username,
                'full_name': full_name}

    def format_feedback(self, staticfeedback):
        feedbackdict = super(AdministratorGroupResource, self).format_feedback(staticfeedback)
        feedbackdict['saved_by'] = self._serialize_user(staticfeedback.saved_by)
        feedbackdict['save_timestamp'] = format_datetime(staticfeedback.save_timestamp)
        feedbackdict['points'] = staticfeedback.points
        return feedbackdict


class AggregatedGroupInfo(InstanceMixin, ReadModelMixin, ModelView):
    """
    Provides an API that aggregates a lot of information about a group for
    administrators.

    # GET
    An object with the following attributes:

    - ``id`` (int): Internal Devilry ID of the group. Is never ``null``.
    - ``deadlines`` (list): List of all deadlines and deliveries on the group.
    """
    permissions = (IsAuthenticated, IsGroupAdmin)
    resource = AdministratorGroupResource

    def get_queryset(self):
        qry = super(AggregatedGroupInfo, self).get_queryset()
        qry = qry.select_related('feedback')
        qry = qry.prefetch_related('deadlines',
                                   'deadlines__deliveries',
                                   'deadlines__deliveries__feedbacks',
                                   'deadlines__deliveries__filemetas')
        return qry
