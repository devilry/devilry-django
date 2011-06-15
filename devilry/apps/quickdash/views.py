from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from ..ui.messages import UiMessages
from ..quickdash.dashboardplugin_registry import registry


@login_required
def main(request):
    messages = UiMessages()
    messages.load(request)
    js_set, views = registry.get_views(request)
    return render_to_response('devilry/quickdash/main.django.html', {
            'groups': registry.get_groups(request),
            'views': views,
            'js_set': js_set,
            'messages': messages
            }, context_instance=RequestContext(request))
