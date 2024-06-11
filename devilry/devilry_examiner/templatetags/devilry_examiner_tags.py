from django import template
from django.utils.translation import gettext_lazy
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='formatted_status')
@stringfilter
def formatted_status(value):
    if value == 'waiting-for-feedback':
        return gettext_lazy("Waiting for feedback")
    elif value == 'waiting-for-deliveries':
        return gettext_lazy("Waiting for deliveries")
    elif value == 'no-deadlines':
        return gettext_lazy("No deadlines")
    elif value == 'corrected':
        return gettext_lazy("Corrected")
    elif value == 'closed-without-feedback':
        return gettext_lazy("Closed without feedback")
    return value


@register.filter
def format_is_passing_grade(is_passing_grade):
    if is_passing_grade:
        return gettext_lazy('passed')
    else:
        return gettext_lazy('failed')


@register.filter
def formatted_delivery_count(count):
    if count == 0:
        return gettext_lazy("No deliveries")
    if count == 1:
        return gettext_lazy("{0} delivery received").format(count)
    return gettext_lazy("{0} deliveries received").format(count)


@register.filter(name='status_to_buttontext')
@stringfilter
def status_to_buttontext(value):
    if value == 'waiting-for-feedback':
        return gettext_lazy("Write feedback")
    elif value == 'waiting-for-deliveries':
        return gettext_lazy("Waiting for deliveries")
    elif value == 'no-deadlines':
        return gettext_lazy("No deadlines")
    elif value == 'corrected':
        return gettext_lazy("Show feedback")
    elif value == 'closed-without-feedback':
        return gettext_lazy("Closed without feedback")
    return value


@register.filter
def feedback_to_bootstrapclass(feedback):
    if feedback.is_passing_grade:
        return 'success'
    else:
        return 'warning'


@register.filter
def group_form(value, groupid):
    return value.get_form_by_groupid(groupid)

# @register.simple_tag
# def get_quickmodeform_by_groupid(formcollection, groupid):
#     return formcollection.get_form_by_groupid(groupid)
