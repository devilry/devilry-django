from django.conf import settings

from utils import get_languagecode

class LocaleMiddleware(object):
    """
    """
    def process_request(self, request):
        # For easy debugging
        if settings.DEBUG and 'locale' in request.GET:
            request.currentlocale = request.GET['locale']
            return

        # Prefer languagecode in request.GET
        # - we automatically update the user preferences with this if it exists.
        elif 'languagecode' in request.GET:
            languagecode = request.GET['languagecode']
            if languagecode in settings.DEVILRY_I18N_LANGCODEMAPPING:
                locale = settings.DEVILRY_I18N_LANGCODEMAPPING[languagecode]
                request.currentlocale = locale
                if request.user.is_authenticated():
                    profile = request.user.get_profile()
                    profile.languagecode = languagecode
                return

        # Fall back on getting language code from request.user or HTTP_ACCEPT_LANGUAGE
        languagecode = get_languagecode(request)
        locale = settings.DEVILRY_I18N_LANGCODEMAPPING[languagecode]
        request.currentlocale = locale
