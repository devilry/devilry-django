from django.conf import settings

from utils import get_languagecode

class LocaleMiddleware(object):
    """
    Locale middleware.

    Detects the current locale in this order:

        1. If ``settings.DEBUG`` is ``True`` and 'locale' GET header, use the
           locale in the header.
        2. Use the 'languagecode' in the GET header if it is valid. If the user
           is authenticated, store the language code as their preferred language.
        3. If the user has a valid languagecode in their preferences, use it.
        4. Check the ACCEPT_LANGUAGE HTTP header.

    **2** makes it possible to use ``?languagecode=LANGCODE`` to change the
    language preference.  Valid language codes are those in
    ``DEVILRY_I18N_LANGCODEMAPPING``.

    Preferred language code is stored in the ``languagecode`` field on the user profile.

    Uses :func:`devilry.apps.i18n.utils.get_languagecode`.
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
        languagecode = get_languagecode(request.user, request.META.get('HTTP_ACCEPT_LANGUAGE'))
        locale = settings.DEVILRY_I18N_LANGCODEMAPPING[languagecode]
        request.currentlocale = locale
