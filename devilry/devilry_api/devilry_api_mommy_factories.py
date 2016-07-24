from model_mommy import mommy
from devilry.apps.core import mommy_recipes


def api_key_for_user(user, **kwargs):
    """
    Creates a new api key for e specific user
    Args:
        user: :obj:`~devilry_account.User` owner of the key
        **kwargs:

    Returns:
        :obj:`~devilry_api.APIKey` api key for user

    """
    return mommy.make('devilry_api.APIKey', user=user, **kwargs)


def api_key_infinite_lifetime(user, **kwargs):
    """
    Creates a new api key for a specific user with infinite lifetime
    Args:
        user: :obj:`~devilry_account.User` owner of the key
        **kwargs:

    Returns:
        :obj:`~devilry_api.APIKey` api key for user
    """
    return mommy.make('devilry_api.APIKey', user=user, expiration_date=mommy_recipes.FUTURE_PERIOD_END, **kwargs)
