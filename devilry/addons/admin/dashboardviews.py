from django.template.loader import render_to_string
from django.template import RequestContext
from django.core.urlresolvers import reverse

from devilry.core.models import Node, Subject, Period, Assignment


def list_nodes_generic(request, nodecls, orderby='short_name'):
    clsname = nodecls.__name__.lower()
    return render_to_string('devilry/admin/dashboard/list_nodes.django.html', {
        'clsname': clsname
        }, context_instance=RequestContext(request))

def list_nodes(request, *args, **kwargs):
    return list_nodes_generic(request, Node)

def list_subjects(request, *args, **kwargs):
    return list_nodes_generic(request, Subject)

def list_periods(request, *args, **kwargs):
    return list_nodes_generic(request, Period)

def list_assignments(request, *args, **kwargs):
    return list_nodes_generic(request, Assignment)
