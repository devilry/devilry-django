from djangorestframework.views import ListModelView
from djangorestframework.resources import ModelResource
from djangorestframework.permissions import IsAuthenticated

from devilry.apps.core.models import Delivery
from .helpers import GroupResourceHelpersMixin
from .helpers import format_datetime


class RecentDeliveriesResource(ModelResource, GroupResourceHelpersMixin):
    fields = ('id', 'assignment', 'period', 'subject', 'time_of_delivery')
    model = Delivery

    def assignment(self, instance):
        return self.format_basenode(instance.deadline.assignment_group.parentnode)

    def period(self, instance):
        return self.format_basenode(instance.deadline.assignment_group.parentnode.parentnode)

    def subject(self, instance):
        return self.format_basenode(instance.deadline.assignment_group.parentnode.parentnode.parentnode)

    def time_of_delivery(self, instance):
        return format_datetime(instance.time_of_delivery)


class RecentDeliveriesView(ListModelView):
    """
    Lists the 6 most recent deliveries made by the authenticated user ordered
    by ``time_of_delivery``.

    # GET
    List of objects with the following attributes:

    - ``id`` (int): Internal Devilry ID of the delivery. Is never ``null``.
    - ``assignment`` (object): Information about the assignment.
    - ``period`` (object): Information about the period.
    - ``subject`` (object): Information about the subject.
    - ``time_of_delivery`` (datetime): The datetime when the delivery was made.
    """
    permissions = (IsAuthenticated,)
    resource = RecentDeliveriesResource

    def get_queryset(self):
        qry = Delivery.where_is_candidate(self.request.user)
        qry = qry.order_by('-time_of_delivery')
        return qry[:6]
