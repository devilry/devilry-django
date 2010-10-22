from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseForbidden
from django.template import RequestContext

from devilry.core.models import AssignmentGroup, Period
from devilry.core import pluginloader
from devilry.ui.messages import UiMessages

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



def _user_stats(period, user, assignments_in_period):
    assignments = AssignmentGroup.where_is_candidate(user).filter(
            parentnode__parentnode=period).values_list("scaled_points",
                    "is_passing_grade")
    if len(assignments_in_period) > len(assignments):
        assignments = [(0, False) for a in assignments_in_period]
            
    points = period.student_sum_scaled_points(user)
    return (user, assignments, points,
            period.student_passes_period(user))


def _iter_user_stats(period, users, assignments_in_period):
    for user in users:
        yield _user_stats(period, user, assignments_in_period)

@login_required
def admin_periodstats(request, period_id):
    period = get_object_or_404(Period, id=period_id)
    if not period.can_save(request.user):
        return HttpResponseForbidden("Forbidden")

    users = User.objects.filter(
            candidate__assignment_group__parentnode__parentnode=period).distinct()
    assignments_in_period = period.assignments.all()
    maxpoints = sum([a.pointscale for a in assignments_in_period])

    if users.count() == 0:
        usergrades = None
    else:
        usergrades = _iter_user_stats(period, users, assignments_in_period)

    return render_to_response(
        'devilry/gradestats/admin-periodstats.django.html', {
            'period': period,
            'maxpoints': maxpoints,
            'usergrades': usergrades,
            'mustpass_assignments': period.get_must_pass_assignments(),
            'assignments_in_period': assignments_in_period
        }, context_instance=RequestContext(request))
