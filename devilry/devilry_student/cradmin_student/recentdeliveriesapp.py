from django_cradmin.viewhelpers import objecttable
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django_cradmin import crapp

from devilry.apps.core.models import Delivery
from devilry.devilry_student.cradminextensions.columntypes import DeliverySummaryColumn


DELIVERY_TEMPFILES_TIME_TO_LIVE_MINUTES = getattr(settings, 'DELIVERY_DELIVERY_TEMPFILES_TIME_TO_LIVE_MINUTES', 120)


class DeliverySummaryWithAssignmentColumn(DeliverySummaryColumn):
    template_name = 'devilry_student/cradmin_student/recentdeliveriesapp/'\
        'delivery-summary-with-assignment-column.django.html'


class TimeOfDeliveryColumn(objecttable.DatetimeColumn):
    modelfield = 'time_of_delivery'

    def get_default_order_is_ascending(self):
        return False


class PeriodInfoColumn(objecttable.PlainTextColumn):
    """
    Period info column used for tablets and desktop devices.
    """
    orderingfield = 'deadline__assignment_group__parentnode__parentnode__parentnode__long_name'
    allcells_css_classes = ['hidden-xs']

    def get_header(self):
        return _('Course')

    def render_value(self, delivery):
        group = delivery.assignment_group
        return u'{} - {}'.format(
            group.subject.long_name,
            group.period.long_name)

    def is_sortable(self):
        return False


class PeriodInfoXs(objecttable.PlainTextColumn):
    """
    Period info column used for mobile devices.
    """
    orderingfield = 'deadline__assignment_group__parentnode__parentnode__parentnode__long_name'
    allcells_css_classes = ['visible-xs']

    def get_header(self):
        return _('Course')

    def render_value(self, delivery):
        group = delivery.assignment_group
        return u'{} - {}'.format(
            group.subject.short_name,
            group.period.short_name)

    def is_sortable(self):
        return False


class RecentDeliveriesListView(objecttable.ObjectTableView):
    model = Delivery
    # template_name = 'devilry_student/cradmin_student/recentdeliveriesapp/recent-deliveries-list.django.html'
    context_object_name = 'deliveries'
    columns = [
        DeliverySummaryWithAssignmentColumn,
        PeriodInfoColumn,
        PeriodInfoXs,
        TimeOfDeliveryColumn,
    ]

    def get_queryset_for_role(self, user):
        return Delivery.objects\
            .filter_is_candidate(user)\
            .select_related(
                'deadline',
                'deadline__assignment_group',
                'deadline__assignment_group__parentnode',
                'feedback')

    def get_pagetitle(self):
        return _('Recent deliveries')


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            RecentDeliveriesListView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
