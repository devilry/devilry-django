from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.simplejson import JSONEncoder
from django.db.models import Q
from django import http
from django.template import RequestContext
from django.utils.translation import ugettext as _

from devilry.core.models import Node, Subject, Period, Assignment, \
        AssignmentGroup


def node_json_generic(request, nodecls, editurl_callback, qrycallback,
        pathcallback = lambda n: n.get_path().split('.')):
    maximum = 3
    term = request.GET.get('term', '')
    showall = request.GET.get('all', 'no')

    nodes = nodecls.where_is_admin_or_superadmin(request.user)
    if term != '':
        nodes = nodes.filter(
                qrycallback(term)).distinct()
    allcount = nodes.count()

    name = nodecls.__name__.lower()
    if showall != 'yes':
        nodes = nodes[:maximum]
    l = [dict(
            id = n.id,
            path = pathcallback(n),
            editurl = editurl_callback(n))
        for n in nodes]
    data = JSONEncoder().encode(dict(result=l, allcount=allcount))
    response = http.HttpResponse(data, content_type="text/plain")
    return response


@login_required
def node_json(request):
    return node_json_generic(request, Node,
            editurl_callback = lambda n:
                reverse('devilry-admin-edit_node', args=[str(n.id)]),
            qrycallback = lambda t:
                Q(short_name__istartswith=t),
            pathcallback = lambda n: [n.get_path()])

@login_required
def subject_json(request):
    return node_json_generic(request, Subject,
            editurl_callback = lambda n:
                reverse('devilry-admin-edit_subject', args=[str(n.id)]),
            qrycallback = lambda t:
                Q(short_name__istartswith=t)
                | Q(parentnode__short_name__istartswith=t))

@login_required
def period_json(request):
    return node_json_generic(request, Period,
            editurl_callback = lambda n:
                reverse('devilry-admin-edit_period', args=[str(n.id)]),
            qrycallback = lambda t:
                Q(short_name__istartswith=t)
                | Q(parentnode__short_name__istartswith=t)
                | Q(parentnode__parentnode__short_name__istartswith=t))

@login_required
def assignment_json(request):
    return node_json_generic(request, Assignment,
            editurl_callback = lambda n:
                reverse('devilry-admin-edit_assignment', args=[str(n.id)]),
            qrycallback = lambda t:
                Q(short_name__istartswith=t)
                | Q(parentnode__short_name__istartswith=t)
                | Q(parentnode__parentnode__short_name__istartswith=t)
                | Q(parentnode__parentnode__parentnode__short_name__istartswith=t))


@login_required
def assignmentgroup_json(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not assignment.can_save(request.user):
        return http.HttpResponseForbidden("Forbidden")
    maximum = 3
    term = request.GET.get('term', '')
    showall = request.GET.get('all', 'no')

    groups = assignment.assignmentgroups.all()
    if term != '':
        groups = groups.filter(
            Q(name__contains=term)
            | Q(examiners__username__startswith=term)
            | Q(candidates__student__username__startswith=term)).distinct()
    allcount = groups.count()

    if showall != 'yes':
        groups = groups[:maximum]
    l = [dict(
            id = g.id,
            path = [str(g.id), g.get_candidates(), g.get_examiners(), g.name],
            editurl = reverse('devilry-admin-edit_assignmentgroup',
                args=[assignment_id, str(g.id)]))
        for g in groups]
    data = JSONEncoder().encode(dict(result=l, allcount=allcount))
    response = http.HttpResponse(data, content_type="text/plain")
    return response


def node_json_js_generic(request, clsname, headings, deletemessage):
    return render_to_response('devilry/admin/autocomplete-nodename.js', {
            'jsonurl': reverse('admin-autocomplete-%sname' % clsname),
            'createurl': reverse('devilry-admin-create_%s' % clsname),
            'deleteurl': reverse('devilry-admin-delete_many%ss' % clsname),
            'headings': headings,
            'deletemessage': deletemessage,
            'clsname': clsname},
        context_instance=RequestContext(request),
        mimetype='text/javascript')

def node_json_js(request):
    return node_json_js_generic(request, 'node',
            ["Node"],
            _('This will delete all selected nodes and all subjects, periods, '\
            'assignments, assignment groups, deliveries and feedbacks within '\
            'them.'))

def subject_json_js(request):
    return node_json_js_generic(request, 'subject',
            ["Subject"],
            _('This will delete all selected subjects and all periods, '\
            'assignments, assignment groups, deliveries and feedbacks within '\
            'them.'))

def period_json_js(request):
    return node_json_js_generic(request, 'period',
            ["Subject", "Period"],
            _('This will delete all selected periods and all '\
            'assignments, assignment groups, deliveries and feedbacks within '\
            'them.'))

def assignment_json_js(request):
    return node_json_js_generic(request, 'assignment',
            ["Subject", "Period", "Assignment"],
            _('This will delete all selected assignments and all '\
            'assignment groups, deliveries and feedbacks within '\
            'them.'))
