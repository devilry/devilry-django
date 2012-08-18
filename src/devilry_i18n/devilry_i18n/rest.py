from django import forms
from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated
from django.utils.translation import get_language_info


class LanguageSelectForm(forms.Form):
    languagecode = forms.CharField(required=True)


class LanguageSelect(View):
    """
    Provides an API for selecting the language.

    # GET
    An object with the following attributes:

    - ``languagecode`` (string): The languagecode of the preferred language.
    """
    permissions = (IsAuthenticated,)
    form = LanguageSelectForm

    def get(self, request):
        languagecode = request.user.devilryuserprofile.languagecode
        if not languagecode:
            languagecode = 'en'
        return {'preferred': self._get_language_info(languagecode),
                'available': []}

    def _get_language_info(self, languagecode):
        languageinfo = get_language_info(languagecode)
        return {'languagecode': languagecode,
                'name': languageinfo['name'],
                'name_local': languageinfo['name_local']}

    def put(self, request):
        languagecode = self.CONTENT['languagecode']
        user = self.request.user
        profile = user.devilryuserprofile
        profile.languagecode = languagecode
        profile.save()
        return self.get(request)
