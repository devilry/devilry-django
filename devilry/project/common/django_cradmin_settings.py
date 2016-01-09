"""
The django_cradmin settings used by Devilry.
"""

#: If this is ``False``, we assume that users authenticate via a
#: thirdpary authentication backend, and that users can only be added
#: via that backend.
#:
#: This does not actually enable an authentication backend, it just changes
#: the UI to reflect how users are added.
from devilry.devilry_cradmin import devilry_css_icon_map

DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND = True


DJANGO_CRADMIN_FORGOTPASSWORD_URL = '/devilry_resetpassword/begin'
DJANGO_CRADMIN_RESETPASSWORD_FINISHED_REDIRECT_URL = '/'
DJANGO_CRADMIN_SITENAME = 'Devilry'

DJANGO_CRADMIN_MENU_SCROLL_TOP_FIXED = True

DEVILRY_THEME3_VERSION = '1.0.0'
DJANGO_CRADMIN_THEME_PATH = 'devilry_theme3/{}/styles/' \
                            'cradmin_theme_devilry_mainpages/theme.css'.format(DEVILRY_THEME3_VERSION)
DJANGO_CRADMIN_SUPERUSERUI_THEME_PATH = 'devilry_theme3/{}/styles/' \
                                        'cradmin_theme_devilry_superuserui/theme.css'.format(DEVILRY_THEME3_VERSION)


DJANGO_CRADMIN_CSS_ICON_MAP = devilry_css_icon_map.FONT_AWESOME
