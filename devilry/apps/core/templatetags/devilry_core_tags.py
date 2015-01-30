from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()


@register.filter
def devilry_user_displayname(user):
    if not user:
        return ''
    return user.devilryuserprofile.full_name or user.username


@register.filter
def format_is_passing_grade(is_passing_grade):
    if is_passing_grade:
        return _('passed')
    else:
        return _('failed')


@register.filter
def devilry_feedback_shortformat(staticfeedback):
    if not staticfeedback:
        return ''
    if staticfeedback.grade in ('Passed', 'Failed'):
        return staticfeedback.grade
    else:
        return u'{} ({})'.format(
            staticfeedback.grade,
            format_is_passing_grade(staticfeedback.is_passing_grade))
