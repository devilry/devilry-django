from django.template.loader import render_to_string
from django.template import RequestContext


def list_assignmentgroups(request, *args, **kwargs):
    return render_to_string(
        'devilry/examiner/dashboard/list_assignmentgroups.django.html', {
        }, context_instance=RequestContext(request))
