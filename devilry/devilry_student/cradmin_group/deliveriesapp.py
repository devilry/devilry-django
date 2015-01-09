# from django.utils.translation import ugettext_lazy as _
from django.template import defaultfilters
from django.views.generic import DetailView
from django_cradmin.viewhelpers import objecttable
from django_cradmin import crapp
from django.utils.translation import ugettext_lazy as _

from devilry.apps.core.models import Delivery


class DeliverySummaryColumn(objecttable.SingleActionColumn):
    modelfield = 'number'
    template_name = 'devilry_student/cradmin_group/deliveriesapp/deliverysummarycolumn.django.html'
    context_object_name = 'delivery'

    def get_header(self):
        return _('Summary')

    def get_actionurl(self, delivery):
        return self.view.request.cradmin_app.reverse_appurl('deliverydetails', kwargs={'pk': delivery.pk})

    def is_sortable(self):
        return False


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


class QuerySetForRoleMixin(object):
    def get_queryset_for_role(self, group):
        return Delivery.objects\
            .filter(deadline__assignment_group=group)\
            .select_related('deadline')


class DeliveryListView(QuerySetForRoleMixin, objecttable.ObjectTableView):
    model = Delivery
    columns = [
        DeliverySummaryColumn,
        TimeOfDeliveryColumn,
        DeadlineColumn,
    ]


class DeliveryDetailsView(QuerySetForRoleMixin, DetailView):
    template_name = 'devilry_student/cradmin_group/deliveriesapp/delivery_details.django.html'
    context_object_name = 'delivery'

    def get_queryset(self):
        return self.get_queryset_for_role(self.request.cradmin_role)


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            DeliveryListView.as_view(),
            name=crapp.INDEXVIEW_NAME),
        crapp.Url(
            r'^delivery/(?P<pk>\d+)$',
            DeliveryDetailsView.as_view(),
            name='deliverydetails'),
    ]
