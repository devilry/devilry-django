from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseForbidden

from dbsanity import dbsanity_registry
from django.shortcuts import render_to_response


@login_required
def dbsanity_check(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Forbidden")

    return render_to_response('devilry/adminscripts/dbsanity-check.django.html', {
        'registry': dbsanity_registry
        }, context_instance=RequestContext(request))

@login_required
def dbsanity_fix(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Forbidden")

    return render_to_response('devilry/adminscripts/dbsanity-fix.django.html', {
        'registry': dbsanity_registry
        }, context_instance=RequestContext(request))

