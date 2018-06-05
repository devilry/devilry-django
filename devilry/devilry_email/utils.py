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


def build_feedbackfeed_absolute_url(domain_scheme, group_id, instance_id='devilry_group_student'):
    """
    Build the absolute url to a feedbackfeed.

    Args:
        domain_scheme: The scheme and host. E.g http://www.example.com/.
        group_id: AssignmentGroup id.
        crinstance_id: Cradmin instance id.

    Returns:
        str: Absolute url to feedbackfeed.
    """
    from django_cradmin.crinstance import reverse_cradmin_url
    domain_url_start = domain_scheme.rstrip('/')
    absolute_url = '{}{}'.format(
        domain_url_start,
        reverse_cradmin_url(instanceid=instance_id, appname='feedbackfeed', roleid=group_id)
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
