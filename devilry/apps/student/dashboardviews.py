from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.template import RequestContext
from django.db.models import Max, Count

from ..core.models import AssignmentGroup


def student_important(request, *args, **kwargs):
    max_visible = 3
    now_with_slack = datetime.now() - timedelta(days=1)
    groups = AssignmentGroup.active_where_is_candidate(request.user).filter(
            is_open=True)
    groups = groups.annotate(
            deliverycount=Count("deliveries"),
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
