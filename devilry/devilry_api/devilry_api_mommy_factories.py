from model_mommy import mommy


def api_key_for_user(user, **kwargs):
    """
    Creates a new api key for e specific user
    Args:
        user: :obj:`~devilry_account.User` owner of the key
        **kwargs:

    Returns:
        :obj:`~devilry_api.APIKey`

    """
    return mommy.make('devilry_api.APIKey', user=user, **kwargs)

