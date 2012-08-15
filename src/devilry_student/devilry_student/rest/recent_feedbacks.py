from django.db.models import Count, Max
from djangorestframework.views import ListModelView
from djangorestframework.resources import ModelResource
from djangorestframework.permissions import IsAuthenticated

from devilry.apps.core.models import Delivery
from .helpers import GroupResourceHelpersMixin
from .helpers import format_datetime


class RecentFeedbacksResource(ModelResource, GroupResourceHelpersMixin):
    fields = ('id', 'assignment', 'period', 'subject', 'number',
              'time_of_delivery', 'number_of_feedbacks', 'last_feedback')
    model = Delivery

    def assignment(self, instance):
        return self.format_basenode(instance.deadline.assignment_group.parentnode)

    def period(self, instance):
        return self.format_basenode(instance.deadline.assignment_group.parentnode.parentnode)

    def subject(self, instance):
        return self.format_basenode(instance.deadline.assignment_group.parentnode.parentnode.parentnode)

    def time_of_delivery(self, instance):
        return format_datetime(instance.time_of_delivery)

    def last_feedback(self, instance):
        last_feedback = instance.feedbacks.only('id', 'save_timestamp', 'grade', 'is_passing_grade')[0]
        return {'id': last_feedback.id,
                'save_timestamp': last_feedback.save_timestamp,
                'grade': last_feedback.grade,
                'is_passing_grade': last_feedback.is_passing_grade}


class RecentFeedbacksView(ListModelView):
    """
    Lists the 6 most recent feedbacks for the authenticated user.

    # GET
    List of objects with the following attributes:

    - ``id`` (int): Internal Devilry ID of the delivery. Is never ``null``.
    - ``assignment`` (object): Information about the assignment.
    - ``period`` (object): Information about the period.
    - ``subject`` (object): Information about the subject.
    - ``time_of_delivery`` (datetime): The datetime when the delivery was made.
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
