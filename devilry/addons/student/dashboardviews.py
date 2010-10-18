from django.template.loader import render_to_string
from django.template import RequestContext

from devilry.core.models import AssignmentGroup
from devilry.core.utils.GroupNodes import group_assignmentgroups


def list_assignments(request, *args, **kwargs):
    assignment_groups = AssignmentGroup.active_where_is_candidate(request.user)
    old_assignment_groups = AssignmentGroup.old_where_is_candidate(request.user)

    if assignment_groups.count() == 0 \
            and old_assignment_groups.count() == 0:
        return None

    subjects = group_assignmentgroups(assignment_groups)
    old_subjects = group_assignmentgroups(old_assignment_groups)
    return render_to_string('devilry/student/dashboard/show_assignments.django.html', {
            'subjects': subjects,
            'old_subjects': old_subjects,
            }, context_instance=RequestContext(request))
