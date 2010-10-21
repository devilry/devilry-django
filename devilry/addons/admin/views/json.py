from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.simplejson import JSONEncoder
from django.db.models import Q, Count
from django import http

from devilry.core.models import (Node, Subject, Period, Assignment,
        AssignmentGroup)
from devilry.addons.quickdash import defaults


def node_json_generic(request, nodecls, editurl_callback, qrycallback,
        pathcallback = lambda n: n.get_path().split('.'),
        order_by = ['short_name']):
    maximum = defaults.DEFAULT_DISPLAYNUM
    term = request.GET.get('term', '')
    showall = request.GET.get('all', 'no')

    nodes = nodecls.where_is_admin_or_superadmin(request.user)
    total = nodes.count()
    if term != '':
        terms = term.split("AND")
        filters = [qrycallback(t.strip()) for t in terms]
        nodes = nodes.filter(*filters).distinct()
    nodes = nodes.order_by(*order_by)
    allcount = nodes.count()

    name = nodecls.__name__.lower()
    if showall != 'yes':
        nodes = nodes[:maximum]
    l = [dict(
            id = n.id,
            path = pathcallback(n),
            actions = [dict(
                label = _('edit'),
                url = editurl_callback(n))
            ])
        for n in nodes]
    data = JSONEncoder().encode(dict(
        result = l,
        allcount = allcount,
        total = total))
    response = http.HttpResponse(data, content_type="text/plain")
    return response


@login_required
def node_json(request):
    return node_json_generic(request, Node,
            editurl_callback = lambda n:
                reverse('devilry-admin-edit_node', args=[str(n.id)]),
            qrycallback = lambda t:
                Q(short_name__istartswith=t),
            pathcallback = lambda n: [
                n.get_path(),
                n.get_admins()])

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
                    p.get_admins()],
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
                | Q(parentnode__parentnode__parentnode__short_name__istartswith=t),
            pathcallback = lambda a: [
                    a.get_path(),
                    a.publishing_time.strftime(defaults.DATETIME_FORMAT),
                    a.get_admins()],
            order_by = ['-publishing_time'])



def filter_assignmentgroup(postdata, groupsqry, term):
    if term != '':
        # TODO not username on anonymous assignments
        groupsqry = groupsqry.filter(
            Q(name__contains=term)
            | Q(examiners__username__contains=term)
            | Q(candidates__student__username__contains=term))

    # Status
    if not postdata.get('filter-status-0'):
       groupsqry = groupsqry.exclude(
               status=AssignmentGroup.NO_DELIVERIES)
    if not postdata.get('filter-status-1'):
       groupsqry = groupsqry.exclude(
               status=AssignmentGroup.NOT_CORRECTED)
    if not postdata.get('filter-status-2'):
       groupsqry = groupsqry.exclude(
               status=AssignmentGroup.CORRECTED_NOT_PUBLISHED)
    if not postdata.get('filter-status-3'):
       groupsqry = groupsqry.exclude(
               status=AssignmentGroup.CORRECTED_AND_PUBLISHED)

    # Examiner bulk
    if not postdata.get('filter-examiner_bulk-0'):
        groupsqry = groupsqry.exclude(examiners__isnull=False)
    if not postdata.get('filter-examiner_bulk-1'):
        groupsqry = groupsqry.exclude(examiners__isnull=True)

    # Closed
    if not postdata.get('filter-closed-0'):
        groupsqry = groupsqry.exclude(is_open=False)
    if not postdata.get('filter-closed-1'):
        groupsqry = groupsqry.exclude(is_open=True)

    # Examiner
    for key, v in postdata.iteritems():
        if key.startswith('filter-examiner-'):
            if v:
                groupsqry = groupsqry.exclude(examiners__username=v)

    return groupsqry.distinct()


@login_required
def assignmentgroup_json(request, assignment_id):
    def latestdeliverytime(g):
        d = g.get_latest_delivery_with_feedback()
        if d:
            return d.time_of_delivery.strftime(defaults.DATETIME_FORMAT)
        else:
            return ""

    def get_deadlines(g):
        return '<br />'.join([
            d.deadline.strftime(defaults.DATETIME_FORMAT)
            for d in g.deadlines.all()])

    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not assignment.can_save(request.user):
        return http.HttpResponseForbidden("Forbidden")
    maximum = 25
    term = request.GET.get('term', '')
    showall = request.GET.get('all', 'no')

    groups = assignment.assignmentgroups.all()
    total = groups.count()
    groups = filter_assignmentgroup(request.GET, groups, term)
    allcount = groups.count()

    if showall != 'yes':
        groups = groups[:maximum]
    l = [dict(
            id = g.id,
            path = [
                str(g.id),
                g.get_candidates(),
                g.get_examiners(),
                g.name or '',
                str(g.get_number_of_deliveries()),
                latestdeliverytime(g),
                get_deadlines(g),
                dict(label=g.get_localized_status(),
                    cssclasses=g.get_status_cssclass())],
            actions = [
                {'label': _('edit'),
                    'url': reverse('devilry-admin-edit_assignmentgroup',
                            args=[assignment_id, str(g.id)])},
                {'label': _('examine'),
                    'url': reverse('devilry-examiner-show_assignmentgroup',
                            args=[str(g.id)])}
                ]
            )
        for g in groups]
    data = JSONEncoder().encode(dict(
        result = l,
        allcount = allcount,
        total = total))
    response = http.HttpResponse(data, content_type="text/plain")
    return response
