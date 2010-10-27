from django.template.loader import render_to_string
from django.template import RequestContext

from devilry.core.models import Assignment
from devilry.core.utils.GroupNodes import group_assignments


# AssignmentGroup.where_is_examiner(user).annotate(md=Max("deliveries__time_of_delivery")).filter(status=1).order_by("-md")[:10]

def list_assignments(request, *args, **kwargs):
    assignments = Assignment.active_where_is_examiner(request.user)
    if assignments.count() == 0:
        return None
    subjects = group_assignments(assignments)
    return render_to_string(
        'devilry/examiner/dashboard/show_assignments.django.html', {
            'subjects': subjects,
            }, context_instance=RequestContext(request))
