from django.conf import settings



class LocaleMiddleware(object):
    """
    """
    def process_request(self, request):
        accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        print accept
        #languagecode = get_languagecode()
        #request.LANGUAGE_CODE = translation.get_language()
