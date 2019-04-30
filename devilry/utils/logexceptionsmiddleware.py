import logging

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class TracebackLoggingMiddleware(MiddlewareMixin):
    """Middleware that logs exceptions.

    See http://djangosnippets.org/snippets/421/.

    To enable it, add
    'yourapp.middleware.TracebackLoggingMiddleware' to
    your setting.py's MIDDLEWARE.

    """
    def process_exception(self, request, exception):
        logger.exception(repr(request))

