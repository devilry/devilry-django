from django import template

register = template.Library()


@register.inclusion_tag('devilry_theme3/templatetags/user-verbose-inline.django.html')
def devilry_user_verbose_inline(user):
    """
    Returns the user wrapped in HTML formatting tags perfect for showing
    the user inline.
    """
    return {
        'user': user
    }


@register.inclusion_tag('devilry_theme3/templatetags/users-verbose-inline.django.html')
def devilry_users_verbose_inline(users):
    """
    Returns the provided iterable of user objects HTML formatted.

    Perfect for formatting lists of users inline, such as when showing examiners
    or candidates on a group.
    """
    return {
        'users': users
    }


@register.inclusion_tag('devilry_theme3/templatetags/user-verbose-inline.django.html')
def devilry_status_verbose_inline(status):
    """
    Returns the status wrapped in HTML formatting tags perfect for showing
    the status inline.
    """
    return {
        'status': status.qualifies
    }
