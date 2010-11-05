from datetime import datetime
from django.db.models import Max

from devilry.core.models import AssignmentGroup


def filter_not_corrected(examiner):
    now = datetime.now()
    groups = AssignmentGroup.active_where_is_examiner(examiner)
    not_corrected = groups.filter(
            is_open=True,
            status=1)
    not_corrected = not_corrected.annotate(
            active_deadline=Max('deadlines__deadline'),
            time_of_last_delivery=Max('deliveries__time_of_delivery'))
    not_corrected = not_corrected.filter(
            active_deadline__lt=now).order_by('time_of_last_delivery')
    return not_corrected



def _get_xxx_notcorrected_in_assignment(examiner, delivery, **restrict):
    nc = filter_not_corrected(examiner)
    assignment = delivery.assignment_group.parentnode
    nc = nc.filter(parentnode=assignment, **restrict).exclude(
                    id=delivery.assignment_group.id)
    if nc.count() == 0:
        return None
    else:
        return nc[0].get_latest_delivery()


def get_next_notcorrected_in_assignment(examiner, delivery):
    return _get_xxx_notcorrected_in_assignment(examiner, delivery,
            time_of_last_delivery__gte=delivery.time_of_delivery)

def get_prev_notcorrected_in_assignment(examiner, delivery):
    return _get_xxx_notcorrected_in_assignment(examiner, delivery,
            time_of_last_delivery__lt=delivery.time_of_delivery)
