from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.filter(name='formatted_status')
def formatted_status(value):
    if value == 'waiting-for-feedback':
        return _("Waiting for feedback")
    elif value == 'waiting-for-deliveries':
        return _("Waiting for deliveries")
    elif value == 'no-deadlines':
        return _("No deadlines")
    elif value == 'corrected':
        return _("Corrected")
    elif value == 'closed-without-feedback':
        return _("Closed without feedback")
    return value


@register.filter(name='status_to_buttontext')
def status_to_buttontext(value):
    if value == 'waiting-for-feedback':
        return _("Write feedback")
    elif value == 'waiting-for-deliveries':
        return _("Waiting for deliveries")
    elif value == 'no-deadlines':
        return _("No deadlines")
    elif value == 'corrected':
        return _("Show feedback")
    elif value == 'closed-without-feedback':
        return _("Closed without feedback")
    return value