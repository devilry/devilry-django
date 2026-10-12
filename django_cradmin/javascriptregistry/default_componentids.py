from django.conf import settings


def get_default_component_ids():
    return getattr(
        settings,
        "DJANGO_CRADMIN_DEFAULT_STATIC_COMPONENT_IDS",
        [
            "django_cradmin_javascript",
        ],
    )
