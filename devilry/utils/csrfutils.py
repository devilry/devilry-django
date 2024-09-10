from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


def csrf_exempt_if_configured(view):
    if settings.DEVILRY_SKIP_CSRF_FOR_APIVIEWS:
        return csrf_exempt(view)
    return view
