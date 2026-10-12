from django.contrib.auth import get_user_model


def create_testuser(username=None, password="test", **kwargs):
    user = get_user_model()(username=username, **kwargs)
    user.set_password(password)
    user.save()
    return user
