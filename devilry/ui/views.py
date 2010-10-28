from mimetypes import guess_type

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django import http
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.models import User
from django.utils.simplejson import JSONEncoder
from django.db.models import Q

from devilry.core.models import FileMeta
from templatetags.rst_to_html import rst_to_html

def logout_view(request):
    logout(request)
    return http.HttpResponseRedirect(reverse('login'))


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
                    next = form.cleaned_data.get('next') or \
                            settings.DEVILRY_MAIN_PAGE or '/'
                    return http.HttpResponseRedirect(next)
                else:
                    return http.HttpResponseForbidden("Acount is not active")
            else:
                login_failed = True
    else:
        form = LoginForm(initial={'next': request.GET.get('next')})
    return render_to_response('devilry/ui/login.django.html', {
        'form': form,
        'login_failed': login_failed,
        }, context_instance=RequestContext(request))

@login_required
def download_file(request, filemeta_id):
    filemeta = get_object_or_404(FileMeta, pk=filemeta_id)
    assignment_group = filemeta.delivery.assignment_group
    if not (assignment_group.is_candidate(request.user) \
            or assignment_group.is_examiner(request.user) \
            or request.user.is_superuser \
            or assignment_group.parentnode.is_admin(request.user)):
        return http.HttpResponseForbidden("Forbidden")

    # TODO: make this work on any storage backend
    response = http.HttpResponse(
            FileWrapper(filemeta.read_open()),
            content_type=guess_type(filemeta.filename)[0])
    response['Content-Disposition'] = "attachment; filename=%s" % \
                        filemeta.filename.encode("ascii", 'replace')
    response['Content-Length'] = filemeta.size

    return response

def get_description(u):
    desc = ""
    if u.first_name:
        desc += u.first_name + " "
    if u.last_name:
        desc += u.last_name  + " "
    if u.email:
        desc += "&lt;" + u.email+ "&gt;"
    return desc

# TODO: Should this be available to anyone, or maybe only examiners and admins?
@login_required
def user_json(request):
    term = request.GET['term']
    qry = User.objects.filter(Q(username__istartswith=term) | 
                              Q(first_name__istartswith=term) | 
                              Q(last_name__istartswith=term))
    
    l = [dict(id=u.id, value=u.username, label=u.username, 
              desc=get_description(u)) for u in qry]
    data = JSONEncoder().encode(l)
    response = http.HttpResponse(data, content_type="text/plain")
    return response


@login_required
def preview_rst(request):
    if request.method == 'POST' and 'rst' in request.POST:
        rst = request.POST['rst']
        rst = rst_to_html(rst)
        return render_to_response('devilry/ui/rst_preview.django.html', {
                'rst': rst,
            }, context_instance=RequestContext(request))
    return http.HttpResponseBadRequest('Could not find "rst" in POST-data.')



@login_required
def skintest(request):
    return render_to_response("devilry/ui/skintest.django.html",
            context_instance=RequestContext(request))
