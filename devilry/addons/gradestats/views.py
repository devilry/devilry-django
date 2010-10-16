from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, \
        HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.utils.translation import ugettext as _

from devilry.core.models import AssignmentGroup


@login_required
def userstats(request):
    #period = get_object_or_404(Period, pk=subject_id)
    #if not subject.can_save(request.user):
        #return HttpResponseForbidden("Forbidden")
    from devilry.core.gradeplugin import registry

    def iter():
        assignment_groups = AssignmentGroup.active_where_is_candidate(
                request.user)
        assignment_groups = assignment_groups.order_by(
                "parentnode__parentnode", "parentnode__grade_plugin")
        current_period = None
        plugins = None
        for group in assignment_groups:
            if current_period == None \
                    or current_period.id != group.parentnode.parentnode.id:
                if current_period != None:
                    yield current_period, plugins
                current_period = group.parentnode.parentnode
                current_gradeplugin = None
                plugins = []
            if current_gradeplugin != group.parentnode.grade_plugin:
                current_gradeplugin = group.parentnode.grade_plugin
                ri = registry.getitem(current_gradeplugin)
                final_grade = ri.model_cls.calc_final_grade(current_period,
                        current_gradeplugin, request.user)
                plugins.append((ri, final_grade, []))
            d = group.get_latest_delivery_with_published_feedback()

            value = None
            if d:
                value = d.feedback.get_grade_as_short_string()
            else:
                value = group.get_localized_status()
            plugins[-1][2].append((group, value))
        yield current_period, plugins

    return render_to_response(
        'devilry/gradestats/user.django.html', {
            'periods': iter(),
        }, context_instance=RequestContext(request))
