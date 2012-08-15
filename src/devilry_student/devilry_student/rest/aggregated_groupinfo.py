from math import log
from djangorestframework.views import ModelView
from djangorestframework.mixins import InstanceMixin
from djangorestframework.mixins import ReadModelMixin
from djangorestframework.resources import ModelResource
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.permissions import BasePermission
from djangorestframework.response import ErrorResponse
from djangorestframework import status
from django.core.urlresolvers import reverse

from devilry.apps.core.models import AssignmentGroup
from .helpers import format_datetime
from .helpers import format_timedelta
from .helpers import GroupResourceHelpersMixin



filesize_unit_list = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])
def pretty_filesize(num):
    """ Human friendly file size.
    ref: http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    """
    if num > 1:
        exponent = min(int(log(num, 1024)), len(filesize_unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = filesize_unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'


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



class GroupResource(ModelResource, GroupResourceHelpersMixin):
    fields = ('id', 'name', 'is_open', 'candidates', 'deadlines', 'active_feedback',
              'deadline_handling', 'breadcrumbs')
    model = AssignmentGroup


    def candidates(self, instance):
        return map(self.format_candidate, instance.candidates.all())

    def format_feedback(self, staticfeedback):
        return {'id': staticfeedback.id,
                'rendered_view': staticfeedback.rendered_view,
                'save_timestamp': format_datetime(staticfeedback.save_timestamp),
                'grade': staticfeedback.grade,
                # NOTE: points is not included because students are not supposed to get direct access to points.
                'is_passing_grade': staticfeedback.is_passing_grade}

    def format_filemeta(self, filemeta):
        return {'id': filemeta.id,
                'filename': filemeta.filename,
                'size': filemeta.size,
                'download_url': reverse('devilry-delivery-file-download',
                                        kwargs={'filemetaid': filemeta.id}),
                'pretty_size': pretty_filesize(filemeta.size)}

    def format_delivery(self, delivery):
        timedelta_before_deadline = delivery.deadline.deadline - delivery.time_of_delivery
        delivered_by = None
        if delivery.delivered_by:
            delivered_by = self.format_candidate(delivery.delivered_by)
        return {'id': delivery.id,
                'number': delivery.number,
                'delivered_by': delivered_by,
                'after_deadline': delivery.after_deadline,
                'time_of_delivery': format_datetime(delivery.time_of_delivery),
                'offset_from_deadline': format_timedelta(timedelta_before_deadline),
                'alias_delivery': delivery.alias_delivery_id,
                'feedbacks': map(self.format_feedback, delivery.feedbacks.all()),
                'download_all_url': {'zip': reverse('devilry-delivery-download-all-zip',
                                                    kwargs={'deliveryid': delivery.id})},
                'filemetas': map(self.format_filemeta, delivery.filemetas.all())}

    def format_deliveries(self, deadline):
        return map(self.format_delivery, deadline.deliveries.filter(successful=True))

    def format_deadline(self, deadline):
        return {'id': deadline.id,
                'deadline': format_datetime(deadline.deadline),
                'text': deadline.text,
                'deliveries': self.format_deliveries(deadline)}

    def deadlines(self, instance):
        return map(self.format_deadline, instance.deadlines.all())

    def active_feedback(self, instance):
        """
        The active feedback is the feedback that was saved last.
        """
        if instance.feedback:
            return {'feedback': self.format_feedback(instance.feedback),
                    'deadline_id': instance.feedback.delivery.deadline_id,
                    'delivery_id': instance.feedback.delivery_id}
        else:
            return None

    def deadline_handling(self, instance):
        return instance.parentnode.deadline_handling

    def breadcrumbs(self, instance):
        return {'assignment': self.format_basenode(instance.parentnode),
                'period': self.format_basenode(instance.parentnode.parentnode),
                'subject': self.format_basenode(instance.parentnode.parentnode.parentnode)}


class AggregatedGroupInfo(InstanceMixin, ReadModelMixin, ModelView):
    """
    Provides an API that aggregates a lot of information about a group.

    # GET
    An object with the following attributes:

    - ``id`` (int): Internal Devilry ID of the group. Is never ``null``.
    - ``name`` (string|null): The name of the group.
    - ``is_open`` (bool): Is the group open?
    - ``candidates`` (list): List of all candidates on the group.
    - ``deadlines`` (list): List of all deadlines and deliveries on the group.
    - ``active_feedback`` (object|null): Information about the active feedback.
    """
    permissions = (IsAuthenticated, IsCandidate)
    resource = GroupResource
