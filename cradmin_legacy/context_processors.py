from django.conf import settings


def get_setting(settingvariable, fallback=None):
    return getattr(settings, settingvariable, fallback)


def get_cradmin_legacy_menu_scroll_top_fixed_setting():
    scroll_top_fixed_settings = get_setting("CRADMIN_LEGACY_MENU_SCROLL_TOP_FIXED", False)
    if scroll_top_fixed_settings is True:
        return {
            "cssClasses": {
                "scrollingClass": "cradmin-legacy-menu-scrolling",
            }
        }
    else:
        return False


def cradmin(request):
    return {
        "CRADMIN_LEGACY_THEME_PATH": get_setting(
            "CRADMIN_LEGACY_THEME_PATH", "cradmin_legacy/dist/css/cradmin_theme_default/theme.css"
        ),
        "CRADMIN_LEGACY_MENU_SCROLL_TOP_FIXED": get_cradmin_legacy_menu_scroll_top_fixed_setting(),
        "CRADMIN_LEGACY_MOMENTJS_LOCALE": get_setting("CRADMIN_LEGACY_MOMENTJS_LOCALE", None),
        "CRADMIN_LEGACY_CSS_ICON_LIBRARY_PATH": get_setting(
            "CRADMIN_LEGACY_CSS_ICON_LIBRARY_PATH",
            "cradmin_legacy/dist/vendor/fonts/fontawesome/css/font-awesome.min.css",
        ),
        "CRADMIN_LEGACY_HIDE_PAGE_HEADER": get_setting("CRADMIN_LEGACY_HIDE_PAGE_HEADER", False),
    }
