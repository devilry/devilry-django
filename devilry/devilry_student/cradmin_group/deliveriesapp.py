# from django.utils.translation import ugettext_lazy as _
from django.template import defaultfilters
from django_cradmin.viewhelpers import objecttable
from django_cradmin import crapp
from django.utils.translation import ugettext_lazy as _

from devilry.apps.core.models import Delivery


class DeliveryNumberColumn(objecttable.SingleActionColumn):
    modelfield = 'number'

    def get_actionurl(self, obj):
        return '#'

    def get_default_order_is_ascending(self):
        return None

    def render_value(self, delivery):
        value = super(DeliveryNumberColumn, self).render_value(delivery)
        return _('Delivery #%(number)s') % {'number': value}


class TimeOfDeliveryColumn(objecttable.DatetimeColumn):
    modelfield = 'time_of_delivery'

    def get_default_order_is_ascending(self):
        return None


class DeadlineColumn(objecttable.DatetimeColumn):
    modelfield = 'deadline'
    orderingfield = 'deadline__deadline'

    def render_value(self, delivery):
        return defaultfilters.date(delivery.deadline.deadline, self.datetime_format)

    def get_default_order_is_ascending(self):
        return None


class DeliveryListView(objecttable.ObjectTableView):
    model = Delivery
    columns = [
        DeliveryNumberColumn,
        TimeOfDeliveryColumn,
        DeadlineColumn,
    ]

    def get_queryset_for_role(self, group):
        return Delivery.objects\
            .filter(deadline__assignment_group=group)\
            .select_related('deadline')


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            DeliveryListView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
