import pycountry as pycountry
from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from django.utils import translation
from django.views.generic import TemplateView

from devilry.devilry_account.models import User


class LanguageInfo(object):

    def __init__(self, languagecode, language=None):
        self.languagecode = languagecode
        self.language = language or self.__get_language()

    def __get_language(self):
        try:
            if len(self.languagecode) == 2:
                return pycountry.languages.get(alpha_2=self.languagecode).name
            elif len(self.languagecode) == 3:
                return pycountry.languages.get(alpha_3=self.languagecode).name
        except Exception:
            return self.languagecode
        return self.languagecode


class SelectLanguageView(TemplateView):
    template_name = 'devilry_account/crapps/account/select_language.django.html'

    def post(self, request, *args, **kwargs):
        selected_languagecode = self.__get_selected_languagecode(data=request.POST)
        if request.user.is_authenticated():
            self.__update_user_language_code(request=request, languagecode=selected_languagecode)
            request.session['SELECTED_LANGUAGE_CODE'] = selected_languagecode
        else:
            request.session['SELECTED_LANGUAGE_CODE'] = selected_languagecode
        return HttpResponseRedirect('/account/')

    def __update_user_language_code(self, request, languagecode):
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            raise Http404()
        else:
            user.languagecode = languagecode
            user.full_clean()
            user.save()

    def __get_selected_languagecode(self, data):
        selected_languagecode = data.get('selected_language', None)
        if not selected_languagecode:
            return translation.get_language()

        languagecodes = [language[0] for language in settings.LANGUAGES]
        if selected_languagecode in languagecodes:
            return selected_languagecode
        else:
            return translation.get_language()

    def get_context_data(self, **kwargs):
        context = super(SelectLanguageView, self).get_context_data(**kwargs)
        context['languages'] = self.__get_languages_info()
        return context

    def __get_languages_info(self):
        language_objects_info_list = []
        for language in settings.LANGUAGES:
            language_info = LanguageInfo(
                languagecode=language[0],
                language=language[1]
            )
            if language[0] == translation.get_language():
                language_objects_info_list.insert(0, language_info)
            else:
                language_objects_info_list.append(language_info)
        return language_objects_info_list
