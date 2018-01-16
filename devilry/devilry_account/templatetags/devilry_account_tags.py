from django import template

register = template.Library()


@register.inclusion_tag('devilry_account/templatetags/user-verbose-inline.django.html')
def devilry_user_verbose_inline(user):
    """
    Returns the user wrapped in HTML formatting tags perfect for showing
    the user inline.
    """
    return {
        'user': user
    }


@register.inclusion_tag('devilry_account/templatetags/user-verbose-inline-plain.django.html')
def devilry_user_verbose_inline_plain(user):
    """
    Same as :method:`.devilry_user_verbose_inline` but without html and styling.
    """
    return {
        'user': user
    }


@register.inclusion_tag('devilry_account/templatetags/multiple-users-verbose-inline.django.html')
def devilry_multiple_users_verbose_inline(users):
    """
    Returns the provided iterable of user objects HTML formatted.

    Perfect for formatting lists of users inline, such as when showing examiners
    or candidates on a group.
    """
    return {
        'users': users
    }
