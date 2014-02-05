from datetime import datetime
from math import log
from djangorestframework.views import ModelView
from djangorestframework.mixins import InstanceMixin
from djangorestframework.mixins import ReadModelMixin
from djangorestframework.resources import ModelResource
from djangorestframework.permissions import IsAuthenticated
from django.core.urlresolvers import reverse

from devilry.apps.core.models import AssignmentGroup
from .helpers import format_datetime
from .helpers import format_timedelta
from .helpers import GroupResourceHelpersMixin
from .helpers import IsPublishedAndCandidate



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


class GroupResource(ModelResource, GroupResourceHelpersMixin):
    fields = ('id', 'name', 'is_open', 'candidates', 'deadlines', 'active_feedback',
              'deadline_handling', 'breadcrumbs', 'examiners', 'delivery_types',
              'status', 'is_relatedstudent_on_period', 'students_can_create_groups_now')
    model = AssignmentGroup

    def students_can_create_groups_now(self, instance):
        return instance.assignment.students_can_create_groups_now

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
        now = datetime.now()
        return {'id': deadline.id,
                'deadline': format_datetime(deadline.deadline),
                'in_the_future': deadline.deadline > now,
                'offset_from_now': format_timedelta(now - deadline.deadline),
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


    def examiners(self, instance):
        if instance.parentnode.anonymous:
            return None
        else:
            return map(self.format_examiner, instance.examiners.all())

    def delivery_types(self, instance):
        return instance.parentnode.delivery_types

    def status(self, instance):
        return instance.get_status()

    def is_relatedstudent_on_period(self, instance):
        period = instance.parentnode.parentnode
        user = self.view.request.user
        return period.relatedstudent_set.filter(user=user).exists()

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
    - ``breadcrumbs`` (object): Contains id, long and shortnames of assignment, period and subject.
    """
    permissions = (IsAuthenticated, IsPublishedAndCandidate)
    resource = GroupResource

    def get_queryset(self):
        qry = super(AggregatedGroupInfo, self).get_queryset()
        qry = qry.select_related('feedback',
                                 'parentnode',
                                 'parentnode__parentnode',
                                 'parentnode__parentnode__parentnode')
        qry = qry.prefetch_related('deadlines',
                                   'deadlines__deliveries',
                                   'deadlines__deliveries__feedbacks',
                                   'deadlines__deliveries__filemetas',
                                   'examiners', 'examiners__user',
                                   'examiners__user__devilryuserprofile',
                                   'candidates', 'candidates__student',
                                   'candidates__student__devilryuserprofile')
        return qry
