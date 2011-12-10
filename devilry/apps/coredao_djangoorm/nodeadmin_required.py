from devilry.apps.core.models.node import Node
from devilry.apps.coredao.errors import PermissionDeniedError


def nodeadmin_required(user, errormsg, *nodeids):
    if user.is_superuser:
        return
    for nodeid in nodeids:
        if nodeid == None:
            raise PermissionDeniedError(errormsg)
        if Node.where_is_admin(user).filter(id=nodeid).count() == 0:
            raise PermissionDeniedError(errormsg)
