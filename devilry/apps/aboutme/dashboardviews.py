from django.template.loader import render_to_string
from django.template import RequestContext


def aboutme(request, *args, **kwargs):
    return render_to_string('devilry/aboutme/aboutme.django.html', {
        }, context_instance=RequestContext(request))
