from datetime import datetime
from django.db.models import Max

from devilry.core.models import AssignmentGroup



def filter_not_corrected(examiner):
    """ Get all groups with status 'not corrected' and is_open=True where
    the given user is examiner.
    
    Annotates the active deadline (as active_deadline) and time of last
    delivery (as time_of_delivery), and limits the results to groups with
    active deadline in the past.
    """
    now = datetime.now()
    groups = AssignmentGroup.active_where_is_examiner(examiner)
    not_corrected = groups.filter(
            is_open=True,
            status=1)
    not_corrected = not_corrected.annotate(
            active_deadline=Max('deadlines__deadline'),
            time_of_last_delivery=Max('deliveries__time_of_delivery'))
    not_corrected = not_corrected.filter(
            active_deadline__lt=now)
    return not_corrected



def _get_xxx_notcorrected_in_assignment(examiner, delivery, order_prefix,
        **restrict):
    nc = filter_not_corrected(examiner)
    assignment = delivery.assignment_group.parentnode
    nc = nc.filter(parentnode=assignment, **restrict).exclude(
                    id=delivery.assignment_group.id).order_by(
                            order_prefix+'time_of_last_delivery')
    if nc.count() == 0:
        return None
    else:
        return nc[0].get_latest_delivery()


def get_next_notcorrected_in_assignment(examiner, delivery):
    """
    Takes a delivery and finds the latest delivery of the next group
    (ordered by time_of_delivery of latest delivery) with status 'not
    corrected'.
    
    :return: A :class:`devilry.core.models.Delivery` object or None if there
        is no more 'not corrected' groups where the given user is examiner
        with time_of_delivery greater to or equal to the given delivery.
    """
    return _get_xxx_notcorrected_in_assignment(examiner, delivery, "",
            time_of_last_delivery__gte=delivery.time_of_delivery)

def get_prev_notcorrected_in_assignment(examiner, delivery):
    """
    Takes a delivery and finds the latest delivery of the previous group
    (ordered by time_of_delivery of latest delivery) with status 'not
    corrected'.
    
    :return: A :class:`devilry.core.models.Delivery` object or None if there
        is no more 'not corrected' groups where the given user is examiner
        with time_of_delivery less than the given delivery.
    """
    return _get_xxx_notcorrected_in_assignment(examiner, delivery, "-",
            time_of_last_delivery__lt=delivery.time_of_delivery)
