from django.contrib.auth import authenticate, login, logout
from django import forms
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('admin'))


class LoginForm(forms.Form):
    username = forms.CharField()
    next = forms.CharField(widget=forms.HiddenInput)
    password = forms.CharField(widget=forms.PasswordInput)

def login_view(request):
    login_failed = False
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(form.cleaned_data['next'])
                else:
                    return HttpResponseForbidden("Acount is not active")
            else:
                login_failed = True
    else:
        form = LoginForm(initial={'next': request.GET.get('next')})
    return render_to_response('devilry/ui/login.django.html', {
        'form': form,
        'login_failed': login_failed,
        }, context_instance=RequestContext(request))
