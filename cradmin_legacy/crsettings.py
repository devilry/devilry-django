from django.conf import settings


def get_setting(setting, fallbackvalue=None):
    """
    Get a Django setting falling back to the given ``fallbackvalue``
    if ``settings.<setting>`` is not set.
    """
    return getattr(settings, setting, fallbackvalue)
