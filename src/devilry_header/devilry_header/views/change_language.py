from django.views.generic import View
from django.shortcuts import redirect
from django.conf import settings
from django import forms
from django.http import HttpResponseBadRequest


class ChangeLanguageForm(forms.Form):
    languagecode = forms.ChoiceField(
        choices=settings.LANGUAGES
    )
    redirect_url=forms.CharField()


class ChangeLanguageView(View):
    http_method_names = ['post']

    def post(self, request):
        form = ChangeLanguageForm(self.request.POST)
        if form.is_valid():
            profile = self.request.user.devilryuserprofile
            profile.languagecode = form.cleaned_data['languagecode']
            profile.full_clean()
            profile.save()
            return redirect(form.cleaned_data['redirect_url'])
        else:
            return HttpResponseBadRequest(form.errors.as_text())