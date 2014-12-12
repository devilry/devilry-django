from datetime import datetime
from djangorestframework.views import ListModelView
from djangorestframework.resources import ModelResource
from djangorestframework.permissions import IsAuthenticated

from devilry.apps.core.models import Delivery
from .helpers import GroupResourceHelpersMixin
from .helpers import format_datetime
from .helpers import format_timedelta


class RecentDeliveriesResource(ModelResource, GroupResourceHelpersMixin):
    fields = ('id', 'group', 'assignment', 'period', 'subject',
              'time_of_delivery', 'group', 'number')
    model = Delivery

    def assignment(self, instance):
        return self.format_basenode(instance.deadline.assignment_group.parentnode)

    def period(self, instance):
        return self.format_basenode(instance.deadline.assignment_group.parentnode.parentnode)

    def subject(self, instance):
        return self.format_basenode(instance.deadline.assignment_group.parentnode.parentnode.parentnode)

    def time_of_delivery(self, instance):
        return {'offset_from_now': format_timedelta(datetime.now() - instance.time_of_delivery),
                'datetime': format_datetime(instance.time_of_delivery)}

    def group(self, instance):
        group = instance.deadline.assignment_group
        return {'id': group.id,
                'name': group.name}


class RecentDeliveriesView(ListModelView):
    """
    Lists the 6 most recent deliveries made by the authenticated user ordered
    by ``time_of_delivery``.

    # GET
    List of objects with the following attributes:

    - ``id`` (int): Internal Devilry ID of the delivery. Is never ``null``.
    - ``group`` (object): Information about the group.
    - ``number`` (int): Delivery number.
    - ``assignment`` (object): Information about the assignment.
    - ``period`` (object): Information about the period.
    - ``subject`` (object): Information about the subject.
    - ``time_of_delivery`` (object): The date and time when the delivery was made, including the offset from _now_.
    """
    permissions = (IsAuthenticated,)
    resource = RecentDeliveriesResource

    def get_queryset(self):
        qry = Delivery.where_is_candidate(self.request.user)
        qry = qry.order_by('-time_of_delivery')
        qry = qry.select_related('deadline', 'deadline__assignment_group',
                                 'deadline__assignment_group__parentnode',
                                 'deadline__assignment_group__parentnode__parentnode',
                                 'deadline__assignment_group__parentnode__parentnode__parentnode')
        return qry[:6]
