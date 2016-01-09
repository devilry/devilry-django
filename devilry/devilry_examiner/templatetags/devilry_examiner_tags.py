from django import template
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import stringfilter
from devilry.devilry_gradingsystem.models import FeedbackDraft

register = template.Library()

@register.filter(name='formatted_status')
@stringfilter
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

@register.filter
def format_is_passing_grade(is_passing_grade):
    if is_passing_grade:
        return _('passed')
    else:
        return _('failed')

@register.filter
def formatted_delivery_count(count):
    if count == 0:
        return _("No deliveries")
    if count == 1:
        return _("{0} delivery received").format(count)
    return _("{0} deliveries received").format(count)

@register.filter
def get_feedback_url(assignment):
    return assignment.get_gradingsystem_plugin_api().get_bulkedit_feedback_url(assignment.id)


@register.filter(name='status_to_buttontext')
@stringfilter
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


@register.filter
def feedback_to_bootstrapclass(feedback):
    if feedback.is_passing_grade:
        return 'success'
    else:
        return 'warning'

@register.filter
def group_delivery_status_to_bootstrapclass(group):
    if group.delivery_status == 'waiting-for-something':
        return "muted"
    elif group.delivery_status == 'corrected':
        return feedback_to_bootstrapclass(group.feedback)
    else:
        return "danger"


@register.filter
def group_form(value, groupid):
    return value.get_form_by_groupid(groupid)

# @register.simple_tag
# def get_quickmodeform_by_groupid(formcollection, groupid):
#     return formcollection.get_form_by_groupid(groupid)

@register.assignment_tag(takes_context=True)
def get_last_feedback_draft_for_group(context, group):
    """
    Very inefficient method of getting last feedback draft for a group.

    Should be removed when we implement :issue:`769`.
    """
    request = context['request']
    return FeedbackDraft.get_last_feedbackdraft_for_group(
        assignment=group.assignment,
        group=group,
        user=request.user
    )
