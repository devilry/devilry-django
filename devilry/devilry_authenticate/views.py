from crispy_forms import layout
from crispy_forms.helper import FormHelper
from django.contrib import auth
from django import forms
from django import http
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import render


def logout(request):
    auth.logout(request)
    return http.HttpResponseRedirect(reverse('login'))


class LoginForm(forms.Form):
    username = forms.CharField()
    next = forms.CharField(widget=forms.HiddenInput,
                           required=False)
    password = forms.CharField(widget=forms.PasswordInput)

    # We store the hash in this field on page load (see the template)
    urlhash = forms.CharField(widget=forms.HiddenInput,
                              required=False)


def login(request):
    login_failed = False

    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(username=form.cleaned_data['username'],
                                     password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    if form.cleaned_data['next']:
                        nexturl = form.cleaned_data.get('next')
                        nexturl += form.cleaned_data.get('urlhash')
                    else:
                        nexturl = settings.DEVILRY_URLPATH_PREFIX + '/'
                    return http.HttpResponseRedirect(nexturl)
                else:
                    return http.HttpResponseForbidden("Acount is not active")
            else:
                login_failed = True
    else:
        form = LoginForm(initial={'next': request.GET.get('next')})

    formhelper = FormHelper()
    formhelper.form_tag = False
    formhelper.label_class = 'sr-only'
    formhelper.layout = layout.Layout(
        layout.Field('username', placeholder='Username', css_class='input-lg'),
        layout.Field('password', placeholder='Password', css_class='input-lg'),
        'urlhash',
        'next')
    return render(request,
                  'authenticate/login.django.html',
                  {'form': form,
                   'login_failed': login_failed,
                   'login_message': getattr(settings, 'DEVILRY_LOGIN_MESSAGE', None),
                   'formhelper': formhelper})
