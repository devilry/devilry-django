from django.utils import translation
from django.utils.deprecation import MiddlewareMixin

from devilry.devilry_account.models import User


class LocalMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated():
            user = self.__get_devilry_user(request=request)
            languagecode = user.languagecode
        else:
            languagecode = request.session.get('SELECTED_LANGUAGE_CODE')
        translation.activate(languagecode)
        request.LANGUAGE_CODE = translation.get_language()

    def __get_devilry_user(self, request):
        return User.objects.get(id=request.user.id)

    def process_response(self, request, response):
        response['Content-Language'] = translation.get_language()
        return response
