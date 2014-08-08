from django.conf import settings
from django import forms
from djangorestframework.views import View
from djangorestframework.resources import FormResource
from djangorestframework.permissions import IsAuthenticated
from django.utils.translation import get_language_info
from django.core.exceptions import ValidationError


class LanguageCodeField(forms.CharField):
    def validate(self, languagecode):
        super(LanguageCodeField, self).validate(languagecode)
        languages_dict = dict(settings.LANGUAGES)
        if not languagecode in languages_dict:
            raise ValidationError('Invalid languagecode: {0}'.format(languagecode))


class LanguageSelectForm(forms.Form):
    preferred = LanguageCodeField(required=True)


class LanguageSelectResource(FormResource):
    form = LanguageSelectForm

    def validate_request(self, data, files=None):
        # We want to be able to push what we got from GET, but the extra stuff should be ignored.
        if 'selected' in data:
            del data['selected']
        if 'available' in data:
            del data['available']
        return super(LanguageSelectResource, self).validate_request(data, files)


class LanguageSelect(View):
    """
    Provides an API for selecting the language.

    # GET
    Get the current language of the authenticated user and available languages.

    ## Returns
    An object with the following attributes:

    - ``preferred`` (string|null): The languagecode of the preferred language.
      You should not expect that this is a valid language code. Use
      ``selected`` for that.
    - ``selected`` (object): The selected language (languagecode and translated name).
      This is always a valid language.
    - ``available`` (list): List of objects with language info for each available language.


    # Put
    Change the preferred language of the authenticated user.

    ## Parameters

    - ``languagecode`` (string): The languagecode to set as preferred language.

    ## Returns

    - ``languagecode`` (string): The languagecode that was set as preferred
      language (always the same as the input parameter).
    """
    permissions = (IsAuthenticated,)
    resource = LanguageSelectResource

    def get(self, request):
        preferred = request.user.devilryuserprofile.languagecode
        languagecode = request.LANGUAGE_CODE
        return {'preferred': preferred,
                'selected': self._get_language_info(languagecode),
                'available': self._formatAvailable()}

    def _formatAvailable(self):
        return [self._get_language_info(languagecode) for languagecode, name in settings.LANGUAGES]

    def _get_language_info(self, languagecode):
        languageinfo = get_language_info(languagecode)
        return {'languagecode': languagecode,
                'name': languageinfo['name_local']}

    def put(self, request):
        languagecode = self.CONTENT['preferred']
        user = self.request.user
        profile = user.devilryuserprofile
        profile.languagecode = languagecode
        profile.save()
        return self.get(request)
