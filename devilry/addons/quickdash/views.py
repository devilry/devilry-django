from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from devilry.ui.messages import UiMessages

from devilry.addons.quickdash.dashboardplugin_registry import registry


@login_required
def main(request):
    messages = UiMessages()
    messages.load(request)
    groups = registry.parsegroups(request)
    focus_id = request.session.get('quickdash-focus-id', None)
    if not focus_id and groups:
        focus_id = groups[0][1][0][0].getid()
    return render_to_response('devilry/quickdash/main.django.html', {
            'groups': groups,
            'focus_id': focus_id,
            'messages': messages
            }, context_instance=RequestContext(request))

@login_required
def set_focus(request):
    id = request.GET.get('id')
    if id:
        request.session['quickdash-focus-id'] = id
        return HttpResponse("ok", content_type="text/plain")
    return HttpResponse("missing id", content_type="text/plain")
