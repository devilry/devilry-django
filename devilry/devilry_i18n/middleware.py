from django.conf import settings
from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin


class LocaleMiddleware(MiddlewareMixin):
    """
    Locale selecting middleware that will look at the languagecode in the
    DevilryUserProfile of the authenticated user.

    Must be added to ``settings.MIDDLEWARE`` after
    ``django.contrib.auth.middleware.AuthenticationMiddleware``.
    """

    def _get_language(self, request):
        if request.user.is_authenticated:
            languagecode = request.user.languagecode
            if languagecode:
                languages_dict = dict(settings.LANGUAGES)
                if languagecode in languages_dict:
                    return languagecode
        return settings.LANGUAGE_CODE

    def process_request(self, request):
        language = self._get_language(request)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        language = translation.get_language()
        translation.deactivate()
        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = language
        return response
