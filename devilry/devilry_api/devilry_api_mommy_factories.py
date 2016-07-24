from model_mommy import mommy
from devilry.apps.core import mommy_recipes
from devilry.devilry_api.models import APIKey


def api_key_short_lifetime(user, **kwargs):
    """
    Creates a api key for a specific user with short lifetime.
    Args:
        user: :obj:`~devilry_account.User` owner of the key
        **kwargs:

    Returns:
        :obj:`~devilry_api.APIKey` api key for user
    """
    return mommy.make('devilry_api.APIKey', user=user, lifetime=APIKey.LIFETIME_SHORT, **kwargs)


def api_key_long_lifetime(user, **kwargs):
    """
    Creates a api key for a specific user with long lifetime.
    Args:
        user: :obj:`~devilry_account.User` owner of the key
        **kwargs:

    Returns:
        :obj:`~devilry_api.APIKey` api key for user
    """
    return mommy.make('devilry_api.APIKey', user=user, lifetime=APIKey.LIFETIME_LONG, **kwargs)


def api_key_expired(user, **kwargs):
    """
    Creates a api key for a specific user that has expired.
    Args:
        user: :obj:`~devilry_account.User` owner of the key
        **kwargs:

    Returns:
        :obj:`~devilry_api.APIKey` api key for user
    """
    return mommy.make('devilry_api.APIKey', user=user, created_datetime=mommy_recipes.OLD_PERIOD_START, **kwargs)


def api_key_student_permission_read(user, **kwargs):
    """
    Creates a api key for a specific user that has student read persmission.
    Args:
        user: :obj:`~devilry_account.User` owner of the key
        **kwargs:

    Returns:
        :obj:`~devilry_api.APIKey` api key for user
    """
    return mommy.make('devilry_api.APIKey', user=user, student_permission=APIKey.STUDENT_PERMISSION_READ, **kwargs)


def api_key_examiner_permission_read(user, **kwargs):
    """
    Creates a api key for a specific user that has examiner read persmission.
    Args:
        user: :obj:`~devilry_account.User` owner of the key
        **kwargs:

    Returns:
        :obj:`~devilry_api.APIKey` api key for user
    """
    return mommy.make('devilry_api.APIKey', user=user, examiner_permission=APIKey.EXAMINER_PERMISSION_READ, **kwargs)


def api_key_admin_permission_read(user, **kwargs):
    """
    Creates a api key for a specific user that has admin read persmission.
    Args:
        user: :obj:`~devilry_account.User` owner of the key
        **kwargs:

    Returns:
        :obj:`~devilry_api.APIKey` api key for user
    """
    return mommy.make('devilry_api.APIKey', user=user, admin_permission=APIKey.ADMIN_PERMISSION_READ, **kwargs)

