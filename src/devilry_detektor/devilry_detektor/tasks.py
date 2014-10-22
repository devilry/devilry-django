from celery import task
from celery.utils.log import get_task_logger

from devilry_detektor.models import DetektorAssignment


logger = get_task_logger(__name__)


@task()
def run_detektor_on_assignment(assignment_id):
    detektorassignment = DetektorAssignment.objects\
        .select_related('assignment')\
        .get(assignment_id=assignment_id)
    logger.info('run_detektor_on_assignment on assignment: id=%s (%s)',
                assignment_id, detektorassignment.assignment)

    if detektorassignment.processing_started_datetime is None:

        # TODO: Process all deliveries within the assignment
        logger.info('run_detektor_on_assignment processing all deliveries on %s requested by %s',
                    detektorassignment.assignment, detektorassignment.processing_started_by)

        detektorassignment.processing_started_datetime = None
        detektorassignment.save()
    else:
        logger.warn('run_detektor_on_assignment for assignment %s aborted because it is already running',
                    detektorassignment.assignment)
