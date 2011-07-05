from ...simplified import simplified_modelapi, PermissionDenied, FieldSpec
from ..core import models



class CanSaveAuthMixin(object):
    @classmethod
    def write_authorize(cls, user, obj):
        if not obj.can_save(user):
            raise PermissionDenied()

    @classmethod
    def read_authorize(cls, user, obj):
        if not obj.can_save(user):
            raise PermissionDenied()


@simplified_modelapi
class SimplifiedNode(CanSaveAuthMixin):
    """ Facade to simplify administrator actions on
    :class:`devilry.apps.core.models.Node`.

    Example:

    .. code-block::

        from django.contrib.auth.models import User
        from devilry.apps.simplified.administrator import SimplifiedNode

        grandma = User.objects.get(username='grandma') # Would usually get this from request.user

        n = SimplifiedNode.create(grandma, short_name='mytestnode',
            long_name='My Test SimplifiedNode')
        print "Created node:", n.short_name, n.long_name

        print "One result", SimplifiedNode.search(grandma, query='mytest').qryset

        SimplifiedNode.update(grandma, id=n.id, short_name='helloworld')

        print "Empty result:", SimplifiedNode.search(grandma, query='mytest').qryset # Returns nothing
        print "One result:", SimplifiedNode.search(grandma, query='helloworld').qryset

        SimplifiedNode.delete(grandma, id=n.id)
        print "Empty result:", SimplifiedNode.search(grandma, query='helloworld').qryset # Returns nothing
    """

    class Meta:
        model = models.Node
        resultfields = FieldSpec('id', 'short_name', 'long_name', 'parentnode__id')
        searchfields = FieldSpec('short_name', 'long_name')
        methods = ['create', 'insecure_read_model', 'read', 'update', 'delete', 'search']

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        qryset = models.Node.where_is_admin_or_superadmin(user)
        parentnode_id = kwargs.pop('parentnode_id', 'DO_NOT_FILTER')
        if parentnode_id != "DO_NOT_FILTER":
            qryset = qryset.filter(parentnode__id = parentnode_id)
        return qryset


@simplified_modelapi
class SimplifiedSubject(CanSaveAuthMixin):
    class Meta:
        model = models.Subject
        resultfields = FieldSpec('id', 'short_name', 'long_name')
        searchfields = FieldSpec('short_name', 'long_name')
        methods = ['create', 'insecure_read_model', 'read', 'update', 'delete', 'search']

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        qryset = models.Subject.where_is_admin_or_superadmin(user)
        parentnode_id = kwargs.pop('parentnode_id', None)
        if parentnode_id != None:
            qryset = qryset.filter(parentnode__id = parentnode_id)
        return qryset


@simplified_modelapi
class SimplifiedPeriod(CanSaveAuthMixin):
    class Meta:
        model = models.Period
        resultfields = FieldSpec('id', 'short_name', 'long_name', 'parentnode__id',
                'start_time', 'end_time',
                subject = ['parentnode__short_name', 'parentnode__long_name'])
        searchfields = FieldSpec('short_name', 'long_name', 'parentnode__short_name',
                'parentnode__long_name')
        methods = ['create', 'insecure_read_model', 'read', 'update', 'delete', 'search']

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        qryset = models.Period.where_is_admin_or_superadmin(user)
        parentnode__id = kwargs.pop('parentnode__id', None)
        if parentnode__id != None:
            qryset = qryset.filter(parentnode__id = parentnode__id)
        return qryset

@simplified_modelapi
class SimplifiedAssignment(CanSaveAuthMixin):
    class Meta:
        model = models.Assignment
        resultfields = FieldSpec('id', 'short_name', 'long_name', 'parentnode__id',
                                 period = ['parentnode__short_name',
                                           'parentnode__long_name',
                                           'parentnode__parentnode__id'],
                                 subject = ['parentnode__parentnode__short_name',
                                            'parentnode__parentnode__long_name'],
                                 pointfields = ['anonymous', 'must_pass', 'maxpoints',
                                                'attempts'])
        searchfields = FieldSpec('short_name', 'long_name')
        methods = ['create', 'insecure_read_model', 'read', 'update', 'delete', 'search']

    @classmethod
    def create_searchqryset(cls, user, **kwargs):
        qryset = models.Assignment.where_is_admin_or_superadmin(user)
        parentnode__id = kwargs.pop('parentnode__id', None)
        if parentnode__id != None:
            qryset = qryset.filter(parentnode__id = parentnode__id)
        return qryset
