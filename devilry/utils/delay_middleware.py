from django.conf import settings
import time

class DelayMiddleware(object):
    def process_request(self, request):
        time.sleep(settings.DELAY_MIDDLEWARE_TIME)
        return None
    
