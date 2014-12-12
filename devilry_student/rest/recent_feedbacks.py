from datetime import datetime
from django.db.models import Count, Max
from djangorestframework.views import ListModelView
from djangorestframework.resources import ModelResource
from djangorestframework.permissions import IsAuthenticated

from devilry.apps.core.models import Delivery
from .helpers import GroupResourceHelpersMixin
from .helpers import format_datetime
from .helpers import format_timedelta


class RecentFeedbacksResource(ModelResource, GroupResourceHelpersMixin):
    fields = ('id', 'assignment', 'period', 'subject', 'number',
              'last_feedback', 'group')
    model = Delivery

    def assignment(self, instance):
        return self.format_basenode(instance.deadline.assignment_group.parentnode)

    def period(self, instance):
        return self.format_basenode(instance.deadline.assignment_group.parentnode.parentnode)

    def subject(self, instance):
        return self.format_basenode(instance.deadline.assignment_group.parentnode.parentnode.parentnode)

    def last_feedback(self, instance):
        last_feedback = instance.feedbacks.only('id', 'save_timestamp', 'grade', 'is_passing_grade')[0]
        return {'id': last_feedback.id,
                'save_timestamp': format_datetime(last_feedback.save_timestamp),
                'grade': last_feedback.grade,
                'is_passing_grade': last_feedback.is_passing_grade,
                'save_offset_from_now': format_timedelta(datetime.now() - last_feedback.save_timestamp)}

    def group(self, instance):
        group = instance.deadline.assignment_group
        return {'id': group.id,
                'name': group.name}


class RecentFeedbacksView(ListModelView):
    """
    Lists the 6 most recent feedbacks for the authenticated user.

    # GET
    List of objects with the following attributes:

    - ``id`` (int): Internal Devilry ID of the delivery. Is never ``null``.
    - ``assignment`` (object): Information about the assignment.
    - ``period`` (object): Information about the period.
    - ``subject`` (object): Information about the subject.
    - ``number`` (int): Delivery number.
    - ``last_feedback`` (object): Information about the last feedback on the delivery.
    """
    permissions = (IsAuthenticated,)
    resource = RecentFeedbacksResource

    def get_queryset(self):
        qry = Delivery.where_is_candidate(self.request.user)
        qry = qry.annotate(number_of_feedbacks=Count('feedbacks'))
        qry = qry.annotate(last_feedback_timestamp=Max('feedbacks__save_timestamp'))
        qry = qry.filter(number_of_feedbacks__gt=0)
        qry = qry.select_related('deadline', 'deadline__assignment_group',
                                 'deadline__assignment_group__parentnode',
                                 'deadline__assignment_group__parentnode__parentnode',
                                 'deadline__assignment_group__parentnode__parentnode__parentnode')
        qry = qry.order_by('-last_feedback_timestamp')
        return qry[:6]
