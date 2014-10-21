from celery import task
from celery.utils.log import get_task_logger
from datetime import datetime

from devilry.apps.core.models import Assignment
from devilry_detektor.models import DetektorAssignment


logger = get_task_logger(__name__)


@task()
def run_detektor_on_assignment(assignment_id, user_id):
    try:
        assignment = Assignment.objects.get(id=assignment_id)
    except Assignment.DoesNotExist:
        logger.exception('run_detektor_on_assignment - Cound not find assignment with ID=%s', assignment_id)
    else:
        logger.info('run_detektor_on_assignment: id=%s (%s)', assignment_id, assignment)
        detektorassignment, created = DetektorAssignment.objects.get_or_create(assignment_id=assignment_id)
        if detektorassignment.processing_started_datetime is None:
            detektorassignment.processing_started_datetime = datetime.now()
            detektorassignment.processing_started_by_id = user_id
            detektorassignment.save()

            # TODO: Process all deliveries within the assignment
            logger.info('run_detektor_on_assignment processing all deliveries on %s requested by %s',
                        assignment, detektorassignment.processing_started_by)

            detektorassignment.processing_started_datetime = None
            detektorassignment.save()
        else:
            logger.warn('run_detektor_on_assignment for assignment %s aborted because it is already running',
                        assignment)
