from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.simplejson import JSONEncoder
from django.db.models import Q
from django import http

from devilry.core.models import Node, Subject, Period, Assignment
from devilry.addons.dashboard import defaults


def node_json_generic(request, nodecls, editurl_callback, qrycallback,
        pathcallback = lambda n: n.get_path().split('.'),
        order_by = ['short_name']):
    maximum = 7
    term = request.GET.get('term', '')
    showall = request.GET.get('all', 'no')

    nodes = nodecls.where_is_admin_or_superadmin(request.user)
    if term != '':
        nodes = nodes.filter(
                qrycallback(term)).distinct()
    nodes = nodes.order_by(*order_by)
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
                Q(short_name__contains=t)
                | Q(admins__username__contains=t),
            pathcallback = lambda s: [
                    s.short_name,
                    s.get_admins()])

@login_required
def period_json(request):
    return node_json_generic(request, Period,
            editurl_callback = lambda n:
                reverse('devilry-admin-edit_period', args=[str(n.id)]),
            qrycallback = lambda t:
                Q(short_name__istartswith=t)
                | Q(parentnode__short_name__istartswith=t)
                | Q(parentnode__parentnode__short_name__istartswith=t),
            pathcallback = lambda p: [
                    p.parentnode.short_name,
                    p.short_name,
                    p.start_time.strftime(defaults.DATETIME_FORMAT),
                    p.end_time.strftime(defaults.DATETIME_FORMAT)],
            order_by = ['-start_time'])

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
