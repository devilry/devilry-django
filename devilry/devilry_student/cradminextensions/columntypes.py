from django_cradmin import crinstance
from django_cradmin.viewhelpers import objecttable
from django.utils.translation import ugettext_lazy as _


class DeliverySummaryColumn(objecttable.SingleActionColumn):
    modelfield = 'number'
    template_name = 'devilry_student/cradminextensions/columntypes/delivery-summary-column.django.html'
    context_object_name = 'delivery'

    def get_header(self):
        return _('Delivery')

    def get_actionurl(self, delivery):
        return crinstance.reverse_cradmin_url(
            instanceid='devilry_student_group',
            appname='deliveries',
            roleid=delivery.deadline.assignment_group_id,
            viewname='deliverydetails',
            kwargs={'pk': delivery.pk}
        )

    def is_sortable(self):
        return False
