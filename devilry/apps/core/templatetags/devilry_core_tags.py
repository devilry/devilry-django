from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
def devilry_user_displayname(user):
    if not user:
        return ''
    return user.devilryuserprofile.full_name or user.username
