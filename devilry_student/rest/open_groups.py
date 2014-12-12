from datetime import datetime
from django.db.models import Max, Q, Count
from djangorestframework.views import ListModelView
from djangorestframework.resources import ModelResource
from djangorestframework.permissions import IsAuthenticated

from devilry.apps.core.models import AssignmentGroup
from devilry.apps.core.models import Delivery
from .helpers import GroupResourceHelpersMixin
from .helpers import format_datetime
from .helpers import format_timedelta
from .errors import BadRequestError


class OpenGroupsResource(ModelResource, GroupResourceHelpersMixin):
    fields = ('id', 'name', 'assignment', 'period', 'subject', 'deliveries',
              'active_deadline')
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
        timedelta = datetime.now() - deadline.deadline
        return {'id': deadline.id,
                'deadline': format_datetime(deadline.deadline),
                'text': deadline.text,
                'deadline_expired': deadline.deadline < datetime.now(),
                'offset_from_deadline': format_timedelta(timedelta)}


class OpenGroupsView(ListModelView):
    """
    Provides an API with information about all the open groups of the
    authenticated user in an active period.

    # GET

    ## Parameters
    You can get only groups that is within a deadline (the deadline has not
    expired), or only groups where the deadline has expired.
    To use this feature, specify ``only=deadline_expired`` or
    ``only=deadline_not_expired`` in the querystring.

    ## Response
    List of objects with the following attributes:

    - ``id`` (int): Internal Devilry ID of the group. Is never ``null``.
    - ``name`` (string|null): The name of the group.
    - ``assignment`` (object): Information about the assignment.
    - ``period`` (object): Information about the period.
    - ``subject`` (object): Information about the subject.
    - ``active_deadline`` (object): Information about the active deadline.
    - ``deliveries`` (object): Number of deliveries.

    The response is ordered by active deadline, with the groups with oldest
    active deadline first.
    """
    permissions = (IsAuthenticated,)
    resource = OpenGroupsResource

    def get_queryset(self):
        qry = AssignmentGroup.active_where_is_candidate(self.request.user)
        qry = qry.filter(is_open=True)
        qry = qry.filter(parentnode__delivery_types=0) # Only include ELECTRONIC - for now this makes sense, and if we need NON-ELECTRONIC, we make a new API, or add an option to this API.
        qry = qry.annotate(newest_deadline=Max('deadlines__deadline'))
        qry = qry.annotate(deadline_count=Count('deadlines__deadline'))
        qry = qry.filter(deadline_count__gt=0)

        # Only include assignments with one of:
        #   - SOFT deadline handling
        #   - deadline has NOT expired
        qry = qry.filter(Q(parentnode__deadline_handling=0) |
                         Q(newest_deadline__gt=datetime.now()))

        only = self.request.GET.get('only', '')
        if only:
            if only == 'deadline_not_expired':
                qry = qry.filter(newest_deadline__gte=datetime.now())
            elif only == 'deadline_expired':
                qry = qry.filter(newest_deadline__lt=datetime.now())
            else:
                raise BadRequestError('Invalid value for ``only``. Specify one of ``deadline_not_expired`` or ``deadline_expired``.')
        qry = qry.order_by('newest_deadline')
        return qry
