from datetime import datetime
from django.template.loader import render_to_string
from django_cradmin.viewhelpers import objecttable
from django.utils.translation import ugettext_lazy as _


class LastDeadlineColumn(objecttable.PlainTextColumn):
    orderingfield = 'last_deadline_datetime'
    modelfield = 'last_deadline_datetime'

    def get_header(self):
        return _('Deadline')

    def render_value(self, obj):
        deadline_datetime = super(LastDeadlineColumn, self).render_value(obj)
        if deadline_datetime:
            return render_to_string('devilry_student/cradminextensions/columntypes/last-deadline.django.html', {
                'deadline_datetime': deadline_datetime,
                'in_the_future': deadline_datetime > datetime.now()
            })
        else:
            return deadline_datetime
