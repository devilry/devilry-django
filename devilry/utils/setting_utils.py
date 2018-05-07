from django.utils.translation import ugettext

from django.conf import settings
from django.utils import translation


def get_devilry_hard_deadline_info_text(setting_name):
    """
    Get the hard deadline info text from settings based on the current language code.

    Args:
        setting_name: The name of the setting to use.

    Returns:
        str: Info text.
    """
    info_dict = getattr(settings, setting_name, None)
    languagecode = translation.get_language()
    if info_dict and languagecode in info_dict:
        return info_dict[languagecode]
    try:
        default_info = info_dict['__default']
    except KeyError:
        raise ValueError("User error: The {} must contain a '__default' info setting. "
                         "This exists by default and has been wrongly removed during setup.".format(setting_name))
    return ugettext(default_info)
