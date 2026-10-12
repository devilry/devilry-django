from django.contrib.auth import get_user_model


def create_user(username=None, password="test", **kwargs):
    """
    Create a user with the given ``username``.

    .. deprecated:: 1.0.1b8
        Use model_bakery instead.
    """
    user = get_user_model().objects.create(username=username, **kwargs)
    user.set_password(password)
    user.save()
    return user
