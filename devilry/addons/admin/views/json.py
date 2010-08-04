from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.simplejson import JSONEncoder
from django.db.models import Q
from django import http
from django.template import RequestContext

from devilry.core.models import Node, Subject, Period, Assignment


def node_json_generic(request, nodecls, qrycallback):
    maximum = 8
    term = request.GET['term']
    if term == '':
        nodes = nodecls.where_is_admin(request.user)
    else:
        nodes = nodecls.where_is_admin(request.user).filter(
                qrycallback(term)).distinct()
    name = nodecls.__name__.lower()
    def get_editurl(node):
        return reverse('devilry-admin-edit_%s' % name,
                args=[str(node.id)])
    l = [dict(
            short_name = n.short_name,
            long_name = n.long_name,
            path = n.get_path(),
            editurl = get_editurl(n))
        for n in nodes[:maximum]]
    data = JSONEncoder().encode(l)
    response = http.HttpResponse(data, content_type="text/plain")
    return response

@login_required
def nodename_json(request):
    return node_json_generic(request, Node,
            lambda t:
                Q(short_name__istartswith=t) | Q(long_name__istartswith=t))

@login_required
def subjectname_json(request):
    return node_json_generic(request, Subject,
            lambda t:
                Q(short_name__istartswith=t) | Q(long_name__istartswith=t)
                | Q(parentnode__short_name__istartswith=t))

@login_required
def periodname_json(request):
    return node_json_generic(request, Period,
            lambda t:
                Q(short_name__istartswith=t) | Q(long_name__istartswith=t)
                | Q(parentnode__short_name__istartswith=t)
                | Q(parentnode__parentnode__short_name__istartswith=t))

@login_required
def assignmentname_json(request):
    return node_json_generic(request, Assignment,
            lambda t:
                Q(short_name__istartswith=t) | Q(long_name__istartswith=t)
                | Q(parentnode__short_name__istartswith=t)
                | Q(parentnode__parentnode__short_name__istartswith=t)
                | Q(parentnode__parentnode__parentnode__short_name__istartswith=t))


def nodename_json_js_generic(request, clsname):
    return render_to_response('devilry/admin/autocomplete-nodename.js', {
            'jsonurl': reverse('admin-autocomplete-%sname' % clsname),
            'clsname': clsname},
        context_instance=RequestContext(request),
        mimetype='text/javascript')

def nodename_json_js(request):
    return nodename_json_js_generic(request, 'node')
def subjectname_json_js(request):
    return nodename_json_js_generic(request, 'subject')
def periodname_json_js(request):
    return nodename_json_js_generic(request, 'period')
def assignmentname_json_js(request):
    return nodename_json_js_generic(request, 'assignment')
