def get_student_users_in_group(group):
    """
    Fetches all Student-users in group.

    Args:
        group: ``AssignmentGroup``.

    Returns:
        QuerySet: QuerySet of ``User``-objects.
    """
    from django.contrib.auth import get_user_model
    user_queryset = get_user_model().objects \
        .filter(id__in=group.candidates.values_list('relatedstudent__user', flat=True))
    return user_queryset


def get_examiner_users_in_group(group):
    """
    Fetches all Examiner-users in group.

    Args:
        group: ``AssignmentGroup``.

    Returns:
        QuerySet: QuerySet of ``User``-objects.
    """
    from django.contrib.auth import get_user_model
    user_queryset = get_user_model().objects \
        .filter(id__in=group.examiners.values_list('relatedexaminer__user', flat=True))
    return user_queryset


def build_absolute_url_for_email(domain_url_start: str, urlpath: str):
    """
    Build the absolute url for an email.

    Args:
        domain_url_start: The scheme and host. E.g http://www.example.com/.
        urlpath: (relative) URL path.

    Returns:
        str: Absolute url to feedbackfeed.
    """
    domain_url_start = domain_url_start.rstrip('/')
    absolute_url = '{}{}'.format(
        domain_url_start,
        urlpath
    )
    return absolute_url


def activate_translation_for_user(user):
    """
    Activate language for a specific user.

    Activates the language if the `user.languagecode` is a valid language code.

    Note::
        Remember to always user translation.deactivate() after using this function!
    """
    from django.utils import translation
    if user.languagecode:
        if translation.check_for_language(user.languagecode):
            translation.activate(user.languagecode)
