from django_cradmin.viewhelpers import objecttable
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django_cradmin import crapp

from devilry.apps.core.models import StaticFeedback


DELIVERY_TEMPFILES_TIME_TO_LIVE_MINUTES = getattr(settings, 'DELIVERY_DELIVERY_TEMPFILES_TIME_TO_LIVE_MINUTES', 120)


class FeedbackSummaryColumn(objecttable.SingleActionColumn):
    modelfield = 'number'
    template_name = 'devilry_student/cradmin_group/feedbacksapp/feedbacksummarycolumn.django.html'
    context_object_name = 'feedback'

    def get_header(self):
        return _('Summary')

    def get_actionurl(self, delivery):
        return self.view.request.cradmin_app.reverse_appurl('deliverydetails', kwargs={'pk': delivery.pk})

    def is_sortable(self):
        return False


class TimeOfFeedbackColumn(objecttable.DatetimeColumn):
    modelfield = 'time_of_delivery'

    def get_default_order_is_ascending(self):
        return None


class FeedbackListView(objecttable.ObjectTableView):
    model = StaticFeedback
    template_name = 'devilry_student/cradmin_group/feedbacksapp/feedback_list.django.html'
    context_object_name = 'deliveries'
    columns = [
        FeedbackSummaryColumn,
        TimeOfFeedbackColumn,
    ]

    def get_pagetitle(self):
        return _('Deliveries')

    def get_queryset_for_role(self, group):
        return StaticFeedback.objects\
            .filter(delivery__deadline__assignment_group=group)\
            .select_related('delivery')


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            FeedbackListView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
