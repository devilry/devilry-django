from django import template

register = template.Library()

@register.filter(name='formatted_status')
def formatted_status(value):
    if value == 'waiting-for-feedback':
        return "Waiting for feedback"
    elif value == 'waiting-for-deliveries':
        return "Waiting for deliveries"
    elif value == 'no-deadlines':
        return "No deadlines"
    elif value == 'corrected':
        return "Corrected"
    elif value == 'closed-without-feedback':
        return "Closed without feedback"
    return value


@register.filter(name='status_to_buttontext')
def status_to_buttontext(value):
    if value == 'waiting-for-feedback':
        return "Write feedback"
    elif value == 'waiting-for-deliveries':
        return "Waiting for deliveries"
    elif value == 'no-deadlines':
        return "No deadlines"
    elif value == 'corrected':
        return "Show feedback"
    elif value == 'closed-without-feedback':
        return "Closed without feedback"
    return value
