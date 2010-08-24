from django.template.loader import render_to_string
from django.template import RequestContext

from devilry.core.models import Assignment
from devilry.core.utils.GroupNodes import group_assignments


def list_assignmentgroups(request, *args, **kwargs):
    return render_to_string(
        'devilry/examiner/dashboard/list_assignmentgroups.django.html', {
        }, context_instance=RequestContext(request))


def list_assignments(request, *args, **kwargs):
    assignments = Assignment.active_where_is_examiner(request.user)
    subjects = group_assignments(assignments)
    return render_to_string(
        'devilry/examiner/dashboard/show_assignments.django.html', {
            'subjects': subjects,
            }, context_instance=RequestContext(request))
