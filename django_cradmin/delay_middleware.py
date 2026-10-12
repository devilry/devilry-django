import time

from django.conf import settings


class DelayMiddleware(object):
    """
    To use this, you must add the following to your settings:

    - Add ``django_cradmin.delay_middleware.DelayMiddleware`` to ``MIDDLEWARE_CLASSES``.
    - Set ``DJANGO_CRADMIN_DELAY_MIDDLEWARE_MILLISECONDS`` to the number of milliseconds
      delay you want to add to all requests (I.E.: 2000 for 2 seconds).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        delay_seconds = getattr(settings, "DJANGO_CRADMIN_DELAY_MIDDLEWARE_MILLISECONDS", None)
        if delay_seconds:
            time.sleep(delay_seconds / 1000.0)
        return self.get_response(request)
