from django.utils.translation import ugettext_lazy as _
from django_cradmin.viewhelpers import objecttable
from django_cradmin import crapp

from devilry.apps.core.models import Delivery


class TimeOfDeliveryColumn(objecttable.SingleActionColumn):
    modelfield = 'time_of_delivery'

    def get_actionurl(self, obj):
        return '#'


class DeliveryListView(objecttable.ObjectTableView):
    model = Delivery
    columns = [
        TimeOfDeliveryColumn,
    ]
    searchfields = [
        'assignment_group__parentnode__long_name',
        'assignment_group__parentnode__short_name']

    def get_queryset_for_role(self, group):
        return Delivery.objects.filter(deadline__assignment_group=group)


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            DeliveryListView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
