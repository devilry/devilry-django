from djangorestframework.views import ListModelView
from djangorestframework.resources import ModelResource
from djangorestframework.permissions import IsAuthenticated

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Delivery
from .helpers import GroupResourceHelpersMixin
from .helpers import format_datetime


class OpenGroupsResource(ModelResource, GroupResourceHelpersMixin):
    fields = ('id', 'name', 'assignment', 'period', 'subject', 'deliveries', 'active_deadline')
    model = AssignmentGroup

    def assignment(self, instance):
        return self.format_basenode(instance.parentnode)

    def period(self, instance):
        return self.format_basenode(instance.parentnode.parentnode)

    def subject(self, instance):
        return self.format_basenode(instance.parentnode.parentnode.parentnode)

    def deliveries(self, instance):
        return Delivery.objects.filter(deadline__assignment_group=instance,
                                       successful=True).count()

    def active_deadline(self, instance):
        deadline = instance.get_active_deadline()
        return {'id': deadline.id,
                'deadline': format_datetime(deadline.deadline),
                'text': deadline.text}


class OpenGroupsView(ListModelView):
    """
    Provides an API with information about all the open groups of the
    authenticated user in an active period.

    # GET
    An object with the following attributes:

    - ``id`` (int): Internal Devilry ID of the group. Is never ``null``.
    - ``name`` (string|null): The name of the group.
    - ``assignment`` (object): Information about the assignment.
    - ``period`` (object): Information about the period.
    - ``subject`` (object): Information about the subject.
    - ``active_deadline`` (object): Information about the active deadline.
    - ``deliveries`` (object): Number of deliveries.
    """
    permissions = (IsAuthenticated,)
    resource = OpenGroupsResource

    def get_queryset(self):
        qry = AssignmentGroup.active_where_is_candidate(self.request.user)
        qry = qry.filter(is_open=True)
        return qry
