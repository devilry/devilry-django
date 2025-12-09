# Devilry RQ timeout exception handler
from rq.job import Job
from rq.timeouts import JobTimeoutException
import logging

logger = logging.getLogger(__name__)

def rq_timeout_exception_handler(job: Job, *exc_info):
    """
    Handles RQ job timeout exceptions by reporting them (e.g., to Sentry) and printing diagnostic information.
    Args:
        job (Job): The RQ job instance that raised the exception.
        *exc_info: Exception information tuple as returned by sys.exc_info().
    Returns:
        bool: Always returns True to indicate the exception was handled.
    Notes:
        - Only handles JobTimeoutException specifically; other exceptions are ignored.
        - Prints job timeout details for debugging purposes.
    """
    if isinstance(exc_info[1], JobTimeoutException):
        logger.error(
            'Failed to execute RQ task due to timeout Job id: %s, Exception: %s',
            job.id, exc_info[1]
        )
        
    return True