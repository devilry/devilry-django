"""
Re-usable authentification methods.
"""

from django.utils.translation import ugettext as _

from devilry.apps.core.models import (Node,
                                      Subject,
                                      Period,
                                      Assignment,
                                      AssignmentGroup)
from djangorestframework.permissions import BasePermission
from devilry.devilry_subjectadmin.rest.errors import PermissionDeniedError


def _admin_required(nodecls, user, errormsg, objid):
    if user.is_superuser:
        return
    if objid == None:
        raise PermissionDeniedError(errormsg)
    if nodecls.where_is_admin_or_superadmin(user).filter(id=objid).count() == 0:
        raise PermissionDeniedError(errormsg)


def nodeadmin_required(user, nodeid):
    """
    Raise :exc:`devilry_subjectadmin.rest.errors.PermissionDeniedError` unless
    the given ``user`` is admin on all of the given Node.

    :param nodeid: ID of Node to check.
    """
    _admin_required(Node, user, _('Permission denied'),  nodeid)


def subjectadmin_required(user, subjectid):
    """
    Raise :exc:`devilry_subjectadmin.rest.errors.PermissionDeniedError` unless
    the given ``user`` is admin on all of the given Subjects.

    :param subjectid: ID of Subject to check.
    """
    _admin_required(Subject, user, _('Permission denied'),  subjectid)


def periodadmin_required(user, periodid):
    """
    Raise :exc:`devilry_subjectadmin.rest.errors.PermissionDeniedError` unless
    the given ``user`` is admin on all of the given Periods.

    :param periodid: ID of Periods to check.
    """
    _admin_required(Period, user, _('Permission denied'), periodid)


def _assignmentadmin_required(user, assignmentid):
    """
    Raise :exc:`devilry_subjectadmin.rest.errors.PermissionDeniedError` unless
    the given ``user`` is admin on all of the given Assignments.

    :param assignmentid: ID of Assignment to check.
    """
    _admin_required(Assignment, user, _('Permission denied'), assignmentid)



class BaseIsAdmin(BasePermission):
    ID_KWARG = 'id'

    def get_id(self):
        """
        Get the ``id`` from the view kwargs.

        :raise PermissionDeniedError: If the ``id`` can not be determined.
        """
        try:
            return self.view.kwargs[self.ID_KWARG]
        except KeyError, e:
            raise PermissionDeniedError(('The {classname} permission checker '
                                         'requires the ``id`` parameter.').format(classname=self.__class__.__name__))

class IsSubjectAdmin(BaseIsAdmin):
    """
    Djangorestframework permission checker that checks if the requesting user
    has admin-permissions on the subject given as the id kwarg to the
    view.
    """
    def check_permission(self, user):
        subjectid = self.get_id()
        subjectadmin_required(user, subjectid)


class IsPeriodAdmin(BaseIsAdmin):
    """
    Djangorestframework permission checker that checks if the requesting user
    has admin-permissions on the period given as the id kwarg to the
    view.
    """
    def check_permission(self, user):
        periodid = self.get_id()
        periodadmin_required(user, periodid)


class IsAssignmentAdmin(BaseIsAdmin):
    """
    Djangorestframework permission checker that checks if the requesting user
    has admin-permissions on the assignment given as the id kwarg  to the
    view.
    """
    def check_permission(self, user):
        assignmentid = self.get_id()
        _assignmentadmin_required(user, assignmentid)

class IsGroupAdmin(BaseIsAdmin):
    """
    Djangorestframework permission checker that checks if the requesting user
    has admin-permissions on the assignment of the group given as the id kwarg
    to the view.
    """
    def check_permission(self, user):
        groupid = self.get_id()
        try:
            group = AssignmentGroup.objects.get(id=groupid)
        except AssignmentGroup.DoesNotExist:
            raise PermissionDeniedError(_('Permission denied'))
        else:
            if not group.can_save(user):
                raise PermissionDeniedError(_('Permission denied'))
