from datetime import datetime
from devilry.apps.core.models import Assignment


def check_if_last_deadline_has_expired(group):
    """
    Check if the last deadline has expired, returning ``False`` if
    it has not expired, "soft" if it has expired and the assignment
    uses soft deadlines, and "hard" if it has expired and the assignment
    uses hard deadlines.
    """
    assignment = group.parentnode
    if group.last_deadline_datetime < datetime.now():
        if assignment.deadline_handling == Assignment.DEADLINEHANDLING_HARD:
            return 'hard'
        else:
            return 'soft'
    else:
        return False
