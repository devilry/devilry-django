from django.conf import settings
import time
from random import randint

from django.utils.deprecation import MiddlewareMixin


class DelayMiddleware(MiddlewareMixin):
    def process_request(self, request):
        time.sleep(randint(*settings.DELAY_MIDDLEWARE_TIME)/100.0)
        return None
