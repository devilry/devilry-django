from django.template.loader import render_to_string
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


class NaturaltimeAndDateTimeColumn(objecttable.PlainTextColumn):
    datetime_format = 'SHORT_DATETIME_FORMAT'

    def render_value(self, obj):
        datetimeobject = super(NaturaltimeAndDateTimeColumn, self).render_value(obj)
        if datetimeobject:
            return render_to_string(
                'devilry_student/cradminextensions/columntypes/naturaltime-and-datetime-column.django.html', {
                    'datetimeobject': datetimeobject,
                    'datetime_format': self.datetime_format
                })
        else:
            return datetimeobject


class NaturaltimeColumn(objecttable.PlainTextColumn):

    def render_value(self, obj):
        datetimeobject = super(NaturaltimeColumn, self).render_value(obj)
        if datetimeobject:
            return render_to_string(
                'devilry_student/cradminextensions/columntypes/naturaltime-column.django.html', {
                    'datetimeobject': datetimeobject
                })
        else:
            return datetimeobject


class BooleanColumn(objecttable.PlainTextColumn):
    true_label = _('True')
    false_label = _('False')

    def get_true_value(self):
        return self.true_label

    def get_false_value(self):
        return self.false_label

    def boolean_to_value(self, value):
        if value:
            return self.get_true_value()
        else:
            return self.get_false_value()

    def render_value(self, obj):
        value = super(BooleanColumn, self).render_value(obj)
        return self.boolean_to_value(value)


class BooleanYesNoColumn(BooleanColumn):
    true_label = _('Yes')
    false_label = _('No')
