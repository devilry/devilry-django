from django import template

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
