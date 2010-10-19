from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseForbidden
from django.template import RequestContext

from devilry.core.models import AssignmentGroup, Period
from devilry.core.gradeplugin import registry
from devilry.core import pluginloader

pluginloader.autodiscover()

def _iter_periodstats(period, user):
    groups = AssignmentGroup.published_where_is_candidate(user).filter(
            parentnode__parentnode=period)
    for gradeplugin_key, gradeplugin in registry.iteritems():
        groups_in_gradeplugin = groups.filter(
                parentnode__grade_plugin=gradeplugin_key)

        gradestats = gradeplugin.model_cls.gradestats(groups_in_gradeplugin)
        if not gradestats:
            continue
        yield gradeplugin, gradestats

@login_required
def userstats(request, period_id):
    period = get_object_or_404(Period, pk=period_id)
    return render_to_response(
        'devilry/gradestats/user.django.html', {
            'period': period,
            'userobj': request.user,
            'gradesbyplugin': _iter_periodstats(period, request.user),
        }, context_instance=RequestContext(request))


@login_required
def admin_userstats(request, period_id, username):
    period = get_object_or_404(Period, pk=period_id)
    if not period.can_save(request.user):
        return HttpResponseForbidden("Forbidden")
    user = get_object_or_404(User, username=username)

    return render_to_response(
        'devilry/gradestats/admin-user.django.html', {
            'period': period,
            'userobj': user,
            'gradesbyplugin': _iter_periodstats(period, user),
        }, context_instance=RequestContext(request))


def admin_periodstats(request, period_id):
    period = get_object_or_404(Period, id=period_id)
    if not period.can_save(request.user):
        return HttpResponseForbidden("Forbidden")

    users = User.objects.filter(
        candidate__assignment_group__parentnode__parentnode=period).distinct()

    def iter():
        for user in users:
            grades = []
            for key, ri in registry.iteritems():
                finalgrade = ri.model_cls.calc_final_grade(period, key, user)
                if finalgrade:
                    grades.append(finalgrade)
            yield user, grades

    if users.count() == 0:
        usergrades = None
    else:
        usergrades = iter()

    return render_to_response(
        'devilry/gradestats/admin-periodstats.django.html', {
            'period': period,
            'usergrades': usergrades
        }, context_instance=RequestContext(request))
