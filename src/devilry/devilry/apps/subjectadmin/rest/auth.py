"""
Re-usable authentification methods.
"""

from devilry.apps.core.models import (Subject,
                                      Period,
                                      Assignment)
from errors import PermissionDeniedError


def _admin_required(nodecls, user, errormsg, *ids):
    if user.is_superuser:
        return
    for id in ids:
        if id == None:
            raise PermissionDeniedError(errormsg)
        if nodecls.where_is_admin(user).filter(id=id).count() == 0:
            raise PermissionDeniedError(errormsg)


def subjectadmin_required(user, errormsg, *subjectids):
    """
    Raise :exc:`devilry.apps.subjectadmin.rest.errors.PermissionDeniedError` unless
    the given ``user`` is admin on all of the given Subjects.

    :param errormsg: Error message for PermissionDeniedError.
    :param subjectids: ID of Subjects to check.
    """
    _admin_required(Subject, user, errormsg, *subjectids)


def periodadmin_required(user, errormsg, *periodids):
    """
    Raise :exc:`devilry.apps.subjectadmin.rest.errors.PermissionDeniedError` unless
    the given ``user`` is admin on all of the given Periods.

    :param errormsg: Error message for PermissionDeniedError.
    :param periodids: ID of Periods to check.
    """
    _admin_required(Period, user, errormsg, *periodids)


def assignmentadmin_required(user, errormsg, *assignmentids):
    """
    Raise :exc:`devilry.apps.subjectadmin.rest.errors.PermissionDeniedError` unless
    the given ``user`` is admin on all of the given Assignments.

    :param errormsg: Error message for PermissionDeniedError.
    :param assignmentids: ID of Assignments to check.
    """
    _admin_required(Assignment, user, errormsg, *assignmentids)
