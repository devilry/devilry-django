from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.template import RequestContext
from django.db.models import Max, Count

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
    return render_to_string('devilry/student/include/list_assignments.django.html', {
            'subjects': subjects,
            'old_subjects': old_subjects,
            'has_subjects': len(subjects) > 0,
            'has_old_subjects': len(old_subjects) > 0,
            }, context_instance=RequestContext(request))



def student_important(request, *args, **kwargs):
    max_visible = 3
    now_with_slack = datetime.now() - timedelta(days=1)
    groups = AssignmentGroup.active_where_is_candidate(request.user).filter(
            is_open=True,
            status__lt=2)
    groups = groups.annotate(
            deliverycount=Count("deadlines"),
            active_deadline=Max('deadlines__deadline'))
    groups = groups.filter(
                    active_deadline__gt=now_with_slack).order_by(
                            '-active_deadline')[:max_visible]
    if groups.count() == 0:
        return None
    groups = sorted(groups, key=lambda g: g.active_deadline)
    return render_to_string('devilry/student/dashboard/student_important.django.html', {
            'groups': groups,
            }, context_instance=RequestContext(request))
