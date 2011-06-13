from ..core import models
from simplified_api import simplified_api
from can_save_authmixin import CanSaveAuthMixin



@simplified_api
class Node(CanSaveAuthMixin):
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
        resultfields = ['id', 'short_name', 'long_name', 'parentnode__id']
        searchfields = ['short_name', 'long_name']
        methods = ['create', 'read_model', 'read', 'update', 'delete', 'search']

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        qryset = models.Node.where_is_admin_or_superadmin(user)
        parentnode_id = kwargs.pop('parentnode_id', 'DO_NOT_FILTER')
        if parentnode_id != "DO_NOT_FILTER":
            qryset = qryset.filter(parentnode__id = parentnode_id)
        return qryset


@simplified_api
class Subject(CanSaveAuthMixin):
    class Meta:
        model = models.Subject
        resultfields = ['id', 'short_name', 'long_name']
        searchfields = ['short_name', 'long_name']
        methods = ['create', 'read_model', 'read', 'update', 'delete', 'search']
    
    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        qryset = models.Subject.where_is_admin_or_superadmin(user)
        parentnode_id = kwargs.pop('parentnode_id', 'DO_NOT_FILTER')
        if parentnode_id != "DO_NOT_FILTER":
            qryset = qryset.filter(parentnode__id = parentnode_id)
        return qryset


@simplified_api
class Period(CanSaveAuthMixin):
    class Meta:
        model = models.Period
        resultfields = ['id', 'short_name', 'long_name', 'parentnode__id',
                'start_time', 'end_time']
        searchfields = ['short_name', 'long_name']
        methods = ['create', 'read_model', 'read', 'update', 'delete', 'search']

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        qryset = models.Period.where_is_admin_or_superadmin(user)
        parentnode__id = kwargs.pop('parentnode__id', None)
        if parentnode__id != None:
            qryset = qryset.filter(parentnode__id = parentnode__id)
        return qryset
