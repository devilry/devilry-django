from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from devilry.core.models import AssignmentGroup, Assignment

from dashboardplugin_registry import registry



@login_required
def main(request):
    is_candidate = AssignmentGroup.where_is_candidate(request.user).count() > 0
    is_examiner = AssignmentGroup.where_is_examiner(request.user).count() > 0
    is_admin = Assignment.where_is_admin(request.user).count() > 0
    important = registry.iterimportant(request, is_candidate, is_examiner,
            is_admin)
    normal = registry.iternormal(request, is_candidate, is_examiner,
            is_admin)
    return render_to_response('devilry/dashboard/main.django.html', {
            'important': important,
            'normal': normal,
            }, context_instance=RequestContext(request))
