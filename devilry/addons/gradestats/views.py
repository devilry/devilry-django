from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseForbidden
from django.template import RequestContext

from devilry.core.models import AssignmentGroup, Period
from devilry.core import pluginloader

pluginloader.autodiscover()

def _get_periodstats(period, user):
    groups = AssignmentGroup.published_where_is_candidate(user).filter(
            parentnode__parentnode=period)
    s = sum([g.scaled_points for g in groups])
    return s, groups

@login_required
def userstats(request, period_id):
    period = get_object_or_404(Period, pk=period_id)
    total, groups = _get_periodstats(period, request.user)
    return render_to_response(
        'devilry/gradestats/user.django.html', {
            'period': period,
            'userobj': request.user,
            'total': total,
            'groups': groups,
        }, context_instance=RequestContext(request))


@login_required
def admin_userstats(request, period_id, username):
    period = get_object_or_404(Period, pk=period_id)
    if not period.can_save(request.user):
        return HttpResponseForbidden("Forbidden")
    user = get_object_or_404(User, username=username)
    total, groups = _get_periodstats(period, user)
    return render_to_response(
        'devilry/gradestats/admin-user.django.html', {
            'period': period,
            'userobj': user,
            'total': total,
            'groups': groups,
        }, context_instance=RequestContext(request))


@login_required
def admin_periodstats(request, period_id):
    period = get_object_or_404(Period, id=period_id)
    if not period.can_save(request.user):
        return HttpResponseForbidden("Forbidden")

    users = User.objects.filter(
        candidate__assignment_group__parentnode__parentnode=period).distinct()
    assignments_in_period = period.assignments.all()
    maxpoints = sum([a.pointscale for a in assignments_in_period])

    def iter():
        full = []
        for user in users:
            points = 0
            assignments = []
            for assignment in assignments_in_period:
                groups = assignment.assignmentgroups.filter(
                        candidates__student=user)
                assignmentpoints = 0
                for group in groups:
                    points += group.scaled_points
                    assignmentpoints += group.scaled_points
                assignments.append((assignment, assignmentpoints, groups))
            yield user, assignments, points

    if users.count() == 0:
        usergrades = None
    else:
        usergrades = iter()

    return render_to_response(
        'devilry/gradestats/admin-periodstats.django.html', {
            'period': period,
            'maxpoints': maxpoints,
            'usergrades': usergrades,
            'assignments_in_period': assignments_in_period
        }, context_instance=RequestContext(request))
