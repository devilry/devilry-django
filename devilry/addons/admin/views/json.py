from django.contrib.auth.models import User
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

    groupsqry = groupsqry.distinct()
    orders = {2:"name", 3:"status"}
    ordercol = int(postdata.get('ordercol', -1))
    if ordercol != -1:
        orderby = orders.get(ordercol)
        if orderby:
            prefix = ""
            orderdir = postdata.get('orderdir', 'asc')
            if orderdir == "desc":
                prefix = "-"
            groupsqry = groupsqry.order_by(prefix + orderby)
    return groupsqry



def _assignmentgroups_json_configure(assignment):
    examiners = User.objects.filter(examiners__parentnode=assignment).distinct()
    data = JSONEncoder().encode(dict(
        showall_label = _("Show all"),
        headings = ["Candidates", "Examiners", "Name", "Status"],
        sortcolumns = [3],
        buttons = {
            "deleteselected": {
                'label': _("Delete selected"),
                'classes': ['delete'],
                'confirmtitle': _("Confirm delete"),
                'confirmlabel': _("Confirm delete"),
                'cancel_label': _("Cancel"),
                'confirm_message': _("This will delete all selected assignmentgroups and all deliveries and feedbacks within them."),
                'url': reverse("devilry-admin-delete_manyassignmentgroups",
                    args=[str(assignment.id)])
            },
            "cleardeadlines": {
                'label': _("Clear deadlines"),
                'classes': ['delete'],
                'confirmtitle': _("Clear deadlines from selected?"),
                'confirmlabel': _("Clear deadlines"),
                'cancel_label': _("Cancel"),
                'confirm_message': _("This will delete all deadlines on all selected assignmentgroups."),
                'url': reverse("devilry-admin-clear_deadlines",
                    args=[str(assignment.id)])
            },
            "createdeadline": {
                'label': _("Create/replace deadline"),
                'url': reverse("devilry-admin-create_deadline",
                    args=[str(assignment.id)])
            },
            "setexaminers": {
                'label': _("Set examiners"),
                'url': reverse("devilry-admin-set_examiners",
                    args=[str(assignment.id)])
            },
            "random_dist_examiners": {
                'label': _("Randomly distribute examiners"),
                'url': reverse("devilry-admin-random_dist_examiners",
                    args=[str(assignment.id)])
            }
        },
        links = {
            'createnew': {
                'label': _("Create new"),
                'url': reverse("devilry-admin-create_assignmentgroup",
                    args=[str(assignment.id)])
            },
            'createmany': {
                'label': _("Create many (advanced)"),
                'url': reverse("devilry-admin-create_assignmentgroups",
                    args=[str(assignment.id)])
            },
            'copygroups': {
                'label': _("Create by copy"),
                'url': reverse("devilry-admin-copy_groups",
                    args=[str(assignment.id)])
            },
        },
        filters = {
          "status": {
            "title": _("Status"),
            "choices": [
              {"label": "No deliveries", "enabled": True},
              {"label": "Not corrected", "enabled": True},
              {"label": "Corrected, not published", "enabled": True},
              {"label": "Corrected and published", "enabled": True}
            ],
          },
          "examiner_bulk": {
            "title": _("Has examiner(s)?"),
            "choices": [
              {"label": "Yes", "enabled": True},
              {"label": "No", "enabled": True},
            ],
          },
          "closed": {
            "title": _("Closed"),
            "choices": [
              {"label": "Yes", "enabled": True},
              {"label": "No", "enabled": True},
            ],
          },
          "examiner": {
            "title": _("Exclude examiner"),
            "choices": [
                {"label": examiner.username,
                    "enabled": False,
                    "value": examiner.username}
                for examiner in examiners],
        
          }
        }
    ))
    response = http.HttpResponse(data, content_type="text/plain")
    return response


@login_required
def assignmentgroups_json(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not assignment.can_save(request.user):
        return http.HttpResponseForbidden("Forbidden")

    if "configure" in request.GET:
        return _assignmentgroups_json_configure(assignment)

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
            cssclass = g.get_status_cssclass(),
            path = [
                g.get_candidates(),
                g.get_examiners(),
                g.name or '',
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
        total = total,
    ))
    response = http.HttpResponse(data, content_type="text/plain")
    return response
