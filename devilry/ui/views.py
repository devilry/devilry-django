from mimetypes import guess_type
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from devilry.core.models import FileMeta


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


class LoginForm(forms.Form):
    username = forms.CharField()
    next = forms.CharField(widget=forms.HiddenInput,
            required=False)
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
                    next = form.cleaned_data.get('next') or settings.DEVILRY_MAIN_PAGE
                    return HttpResponseRedirect(next)
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


#@login_required
#def download_file(request, filemeta_id):
    #filemeta = get_object_or_404(FileMeta, pk=filemeta_id)
    #response = HttpResponse(FileWrapper(
            #file(filemeta.store._get_filepath(filemeta))), content_type='application/zip')
    #response['Content-Disposition'] = "attachment; filename=" + filemeta.filename
    #response['Content-Length'] = filemeta.size

    #return response

@login_required
def download_file(request, filemeta_id):
    filemeta = get_object_or_404(FileMeta, pk=filemeta_id)
    response = HttpResponse(FileWrapper(
            file(filemeta.store._get_filepath(filemeta))),
            content_type=guess_type(filemeta.filename)[0])
    response['Content-Disposition'] = "attachment; filename=" + filemeta.filename
    response['Content-Length'] = filemeta.size

    return response
