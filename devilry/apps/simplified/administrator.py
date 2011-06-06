from ..core import models
from simplified_api import simplified_api
from exceptions import PermissionDenied



@simplified_api
class Node:
    """ Facade to simplify administrator actions on
    :class:`devilry.apps.core.models.Node`.

    Example:

    .. code-block::

        from django.contrib.auth.models import User
        from devilry.apps.simplified.administrator import Node

        grandma = User.objects.get(username='grandma') # Would usually get this from request.user
        n = Node.create(grandma, short_name='mytestnode',
            long_name='My Test Node')
        print "Created node:", n.short_name, n.long_name
        print "One result", Node.search(grandma, query='mytest').qryset
        Node.update(grandma, id=n.id, short_name='helloworld')
        print "Empty result:", Node.search(grandma, query='mytest').qryset # Returns nothing
        print "One result:", Node.search(grandma, query='helloworld').qryset
        Node.delete(grandma, id=n.id)
        print "Empty result:", Node.search(grandma, query='helloworld').qryset # Returns nothing
    """

    class Meta:
        model = models.Node
        search_resultfields = ['id', 'short_name', 'long_name']
        search_searchfields = ['short_name', 'long_name']

    @classmethod
    def _authorize(cls, user, node):
        if not node.can_save(user):
            raise PermissionDenied()

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        qryset = models.Node.where_is_admin_or_superadmin(user)
        parentnode_id = kwargs.pop('parentnode_id', 'DO_NOT_FILTER')
        if parentnode_id != "DO_NOT_FILTER":
            qryset = qryset.filter(parentnode__id = parentnode_id)
        return qryset
