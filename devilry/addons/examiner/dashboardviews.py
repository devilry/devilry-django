from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.template import RequestContext
from django.db.models import Max, Count

from devilry.core.models import AssignmentGroup, Assignment
from devilry.core.utils.GroupNodes import group_assignments



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
    #groups = AssignmentGroup.where_is_admin_or_superadmin(request.user)
    print groups.all()

    not_corrected = groups.filter(
            is_open=True,
            status=1)
    not_corrected = not_corrected.annotate(
            active_deadline=Max('deadlines__deadline'),
            time_of_last_delivery=Max('deliveries__time_of_delivery'))
    not_corrected = not_corrected.filter(
            active_deadline__lt=now).order_by('time_of_last_delivery')
    not_corrected_count = not_corrected.count()
    not_corrected = not_corrected[:3]

    not_published = groups.filter(
            is_open=True,
            status=2)
    not_published = not_published.annotate(
            active_deadline=Max('deadlines__deadline'),
            time_of_last_delivery=Max('deliveries__time_of_delivery'),
            time_of_last_feedback=Max('deliveries__feedback__last_modified'))
    not_published = not_published.order_by('-time_of_last_feedback')
    not_published_count = not_published.count()
    not_published = not_published[:3]

    if not_corrected_count == 0 and not_published_count == 0:
        return None

    return render_to_string(
        'devilry/examiner/dashboard/examiner_important.django.html', {
            'not_corrected_count': not_corrected_count,
            'not_corrected': not_corrected,
            'not_published_count': not_published_count,
            'not_published': not_published,
            }, context_instance=RequestContext(request))
