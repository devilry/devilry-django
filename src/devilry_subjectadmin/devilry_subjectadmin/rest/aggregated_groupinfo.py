from djangorestframework.views import ModelView
from djangorestframework.mixins import InstanceMixin
from djangorestframework.mixins import ReadModelMixin
from djangorestframework.permissions import IsAuthenticated

from devilry_student.rest.aggregated_groupinfo import GroupResource
from .auth import IsGroupAdmin




class AdministratorGroupResource(GroupResource):
    fields = ('id', 'deadlines')


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
