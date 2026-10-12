from django.conf import settings


def get_setting(settingvariable, fallback=None):
    return getattr(settings, settingvariable, fallback)


def get_django_cradmin_menu_scroll_top_fixed_setting():
    scroll_top_fixed_settings = get_setting("DJANGO_CRADMIN_MENU_SCROLL_TOP_FIXED", False)
    if scroll_top_fixed_settings is True:
        return {
            "cssClasses": {
                "scrollingClass": "django-cradmin-menu-scrolling",
            }
        }
    else:
        return False


def cradmin(request):
    return {
        "DJANGO_CRADMIN_MENU_SCROLL_TOP_FIXED": get_django_cradmin_menu_scroll_top_fixed_setting(),
        "DJANGO_CRADMIN_MOMENTJS_LOCALE": get_setting("DJANGO_CRADMIN_MOMENTJS_LOCALE", None),
        "DJANGO_CRADMIN_CSS_ICON_LIBRARY_PATH": get_setting(
            "DJANGO_CRADMIN_CSS_ICON_LIBRARY_PATH",
            "django_cradmin/dist/vendor/fonts/fontawesome/css/font-awesome.min.css",
        ),
        "DJANGO_CRADMIN_HIDE_PAGE_HEADER": get_setting("DJANGO_CRADMIN_HIDE_PAGE_HEADER", False),
    }
