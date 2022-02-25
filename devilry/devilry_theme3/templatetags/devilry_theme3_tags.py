from django import template
from django.templatetags.static import static

import devilry

register = template.Library()


@register.inclusion_tag('devilry_theme3/templatetags/user-verbose-inline.django.html')
def devilry_status_verbose_inline(status):
    """
    Returns the status wrapped in HTML formatting tags perfect for showing
    the status inline.
    """
    return {
        'status': status.qualifies
    }


@register.simple_tag()
def devilry_theme3_dist_path():
    return static('devilry_theme3/{}'.format(devilry.__version__))
