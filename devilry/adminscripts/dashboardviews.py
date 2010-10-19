from django.template.loader import render_to_string
from django.template import RequestContext

def overview(request):
    if not request.user.is_superuser:
        return None

    return render_to_string('devilry/adminscripts/overview.django.html', {
        }, context_instance=RequestContext(request))
