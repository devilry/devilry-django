from model_mommy import mommy
from devilry.apps.core import mommy_recipes
from devilry.devilry_api.models import APIKey


def api_key_short_lifetime(**kwargs):
    """
    Creates a api key with short lifetime.
    Args:
        **kwargs:

    Returns:
        :obj:`~devilry_api.APIKey` api key
    """
    return mommy.make('devilry_api.APIKey', keytype=APIKey.LIFETIME_SHORT, **kwargs)


def api_key_long_lifetime(**kwargs):
    """
    Creates a api key with long lifetime.
    Args:
        **kwargs:

    Returns:
        :obj:`~devilry_api.APIKey` api key
    """
    return mommy.make('devilry_api.APIKey', keytype=APIKey.LIFETIME_LONG, **kwargs)


def api_key_expired(**kwargs):
    """
    Creates a api key that has expired.
    Args:
        **kwargs:

    Returns:
        :obj:`~devilry_api.APIKey` api key
    """
    return mommy.make('devilry_api.APIKey', created_datetime=mommy_recipes.OLD_PERIOD_START, **kwargs)


def api_key_student_permission_read(**kwargs):
    """
    Creates a api key that has student read permission.
    Args:
        **kwargs:

    Returns:
        :obj:`~devilry_api.APIKey` api key
    """
    return mommy.make('devilry_api.APIKey', student_permission=APIKey.STUDENT_PERMISSION_READ, **kwargs)


def api_key_student_permission_write(**kwargs):
    """
    Creates a api key that has student write permission.
    Args:
        **kwargs:

    Returns:
        :obj:`~devilry_api.APIKey` api key
    """
    return mommy.make('devilry_api.APIKey', student_permission=APIKey.STUDENT_PERMISSION_WRITE, **kwargs)


def api_key_examiner_permission_read(**kwargs):
    """
    Creates a api key that has examiner read permission.
    Args:
        **kwargs:

    Returns:
        :obj:`~devilry_api.APIKey` api key
    """
    return mommy.make('devilry_api.APIKey', examiner_permission=APIKey.EXAMINER_PERMISSION_READ, **kwargs)


def api_key_examiner_permission_write(**kwargs):
    """
    Creates a api key that has examiner write permission.

    Returns:
        :obj:`~devilry_api.APIKey` api key
    """
    return mommy.make('devilry_api.APIKey', examiner_permission=APIKey.EXAMINER_PERMISSION_WRITE, **kwargs)


def api_key_admin_permission_read(**kwargs):
    """
    Creates a api key that has admin read permission.
    Args:
        **kwargs:

    Returns:
        :obj:`~devilry_api.APIKey` api key
    """
    return mommy.make('devilry_api.APIKey', admin_permission=APIKey.ADMIN_PERMISSION_READ, **kwargs)
