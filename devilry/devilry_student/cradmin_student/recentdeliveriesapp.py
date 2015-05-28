from django_cradmin.viewhelpers import objecttable
from django.utils.translation import ugettext_lazy as _
from django_cradmin import crapp

from devilry.apps.core.models import deliverytypes
from devilry.apps.core.models import Delivery
from devilry.devilry_student.cradminextensions.columntypes import DeliverySummaryColumn, NaturaltimeAndDateTimeColumn


class DeliverySummaryWithAssignmentColumn(DeliverySummaryColumn):
    template_name = 'devilry_student/cradmin_student/recentdeliveriesapp/'\
        'delivery-summary-with-assignment-column.django.html'


class TimeOfDeliveryColumn(NaturaltimeAndDateTimeColumn):
    modelfield = 'time_of_delivery'
    allcells_css_classes = ['hidden-xs']
    # column_width = '270px'

    # def get_default_order_is_ascending(self):
    #     return False

    def is_sortable(self):
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


class PeriodInfoXsColumn(objecttable.PlainTextColumn):
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
        PeriodInfoXsColumn,
        TimeOfDeliveryColumn,
    ]

    def get_queryset_for_role(self, user):
        return Delivery.objects\
            .filter(delivery_type=deliverytypes.ELECTRONIC)\
            .filter_is_candidate(user)\
            .select_related(
                'deadline',
                'deadline__assignment_group',
                'deadline__assignment_group__parentnode',
                'last_feedback')

    def get_pagetitle(self):
        return _('Recent deliveries')


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            RecentDeliveriesListView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
