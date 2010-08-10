from django.template.loader import render_to_string
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from django.contrib.auth.decorators import login_required
from devilry.core.models import Delivery, AssignmentGroup
from devilry.core.utils.GroupNodes import group_assignmentgroups, print_tree

@login_required
def list_assignments(request, *args, **kwargs):
    assignment_groups = AssignmentGroup.active_where_is_candidate(request.user)
    subjects = group_assignmentgroups(assignment_groups)
    old_assignment_groups = AssignmentGroup.old_where_is_candidate(request.user)
    old_subjects = group_assignmentgroups(old_assignment_groups)
    return render_to_string('devilry/student/dashboard/show_assignments.django.html', {
            'subjects': subjects,
            'old_subjects': old_subjects,
            }, context_instance=RequestContext(request))
