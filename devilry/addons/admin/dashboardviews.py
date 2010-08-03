from django.template.loader import render_to_string
from django.template import RequestContext
from django.core.urlresolvers import reverse

from devilry.core.models import Node, Subject, Period, Assignment


def list_nodes_generic(request, nodecls, orderby='short_name'):
    maximum = 8
    nodes = nodecls.where_is_admin(request.user)[:maximum]
    if nodes.count() == 0:
        return None
    name = nodecls.__name__.lower()
    def get_editurl(node):
        return reverse('devilry-admin-edit_%s' % name,
                args=[str(node.id)])
    if nodes.count() == maximum:
         moreurl = reverse('devilry-admin-list_%ss' % name)
    else:
        moreurl = None
    return render_to_string('devilry/admin/dashboard/list_nodes.django.html', {
        'model_plural_name': nodecls._meta.verbose_name_plural,
        'nodes': [(node, get_editurl(node)) for node in nodes],
        'createurl': reverse('devilry-admin-create_%s' % name),
        'moreurl': moreurl
        }, context_instance=RequestContext(request))


def list_nodes(request, *args):
    return list_nodes_generic(request, Node)

def list_subjects(request, *args):
    return list_nodes_generic(request, Subject)

def list_periods(request, *args):
    return list_nodes_generic(request, Period)

def list_assignments(request, *args):
    return list_nodes_generic(request, Assignment)
