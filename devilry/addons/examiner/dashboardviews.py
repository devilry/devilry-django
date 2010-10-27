from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.template import RequestContext
from django.db.models import Max, Count

from devilry.core.models import AssignmentGroup, Assignment
from devilry.core.utils.GroupNodes import group_assignments


# AssignmentGroup.where_is_examiner(user).annotate(md=Max("deliveries__time_of_delivery")).filter(status=1).order_by("-md")[:10]

def list_assignments(request, *args, **kwargs):
    assignments = Assignment.active_where_is_examiner(request.user)
    if assignments.count() == 0:
        return None
    subjects = group_assignments(assignments)
    return render_to_string(
        'devilry/examiner/include/list_assignments.django.html', {
            'subjects': subjects,
            }, context_instance=RequestContext(request))


def examiner_important(request, *args, **kwargs):
    now = datetime.now()
    groups = AssignmentGroup.active_where_is_examiner(request.user)
    #groups = AssignmentGroup.objects.all()
    groups = groups.filter(
            is_open=True,
            status=1)
    groups = groups.annotate(
            active_deadline=Max('deadlines__deadline'),
            time_of_last_delivery=Max('deliveries__time_of_delivery'))
    groups = groups.filter(
            active_deadline__lt=now).order_by('time_of_last_delivery')
    not_corrected_count = groups.count()
    groups = groups[:3]
    if groups.count() == 0:
        return None

    return render_to_string(
        'devilry/examiner/dashboard/examiner_important.django.html', {
            'not_corrected_count': not_corrected_count,
            'groups': groups,
            }, context_instance=RequestContext(request))
