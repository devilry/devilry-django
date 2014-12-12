from django.conf import settings
import time
from random import randint

class DelayMiddleware(object):
    def process_request(self, request):
        time.sleep(randint(*settings.DELAY_MIDDLEWARE_TIME)/100.0)
        return None
