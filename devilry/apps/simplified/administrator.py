from django.db.models.fields.related import ManyToManyField, RelatedObject

from ..core import models
from base import GetQryResult, SimplifiedBase
from exceptions import PermissionDenied


#def get(cls, user, id):
    #obj = cls._meta.model.objects.get(id=id)
    #cls._authorize(user, obj)
    #return obj

def simplifiedApi(cls):
    bases = tuple([SimplifiedBase] + list(cls.__bases__))
    cls = type(cls.__name__, bases, dict(cls.__dict__))
    meta = cls.Meta
    cls._meta = meta

    throws = [
            ':throws devilry.apps.core.models.Node.DoesNotExist:',
            '   If the node with ``id`` does not exists, or if',
            '   parentnode is not None, and no node with ``id==parentnode_id``',
            '   exists.']

    fields = []
    for fieldname in meta.model._meta.get_all_field_names():
        field = meta.model._meta.get_field_by_name(fieldname)[0]
        if isinstance(field, ManyToManyField):
            pass
        elif isinstance(field, RelatedObject):
            pass
        else:
            if hasattr(field, 'help_text'):
                help_text = field.help_text
            else:
                help_text = ''
            print type(field), field.name, help_text
            fields.append(':param %s: %s' % (field.name, help_text))

    get_doc = '\n'.join(
            ['Get a %(modelname)s object.'] + ['\n'] +
            throws + ['\n\n'] + fields)
    modelname = meta.model.__name__
    cls.get.__func__.__doc__ = get_doc % vars()
    return cls


@simplifiedApi
class Node:
    """ Facade to simplify administrator actions on
    :class:`devilry.apps.core.models.Node`. """
    CORE_MODEL = models.Node

    class Meta:
        model = models.Node

    @classmethod
    def _authorize(cls, user, node):
        if not node.can_save(user):
            raise PermissionDenied()

    @classmethod
    def _set_parentnode_from_id(cls, node, parentnode_id):
        if parentnode_id == None:
            node.parentnode = None
        else:
            node.parentnode = models.Node.objects.get(id=parentnode_id)

    @classmethod
    def create(cls, user, short_name, long_name, parentnode_id=None):
        """ Create a node. """
        node =  models.Node(short_name=short_name, long_name=long_name)
        cls._set_parentnode_from_id(node, parentnode_id)
        cls._authorize(user, node) # Important that this is after parentnode is set, or admins on parentnode will not be permitted!
        node.full_clean()
        node.save()
        return node

    #@classmethod
    #def get(cls, user, id):
        #node = models.Node.objects.get(id=id)
        #cls._authorize(user, node)
        #return node

    @classmethod
    def update(cls, user, id, short_name, long_name,
            parentnode_id=None):
        """ Update the data in the node with the given ``id``.

        :throws devilry.apps.core.models.Node.DoesNotExist:
            If the node with ``id`` does not exists, or if
            parentnode is not None, and no node with ``id==parentnode_id``
            exists.
        :throws django.core.exceptions.ValidationError:
            If the parameters do not validate (see
            :class:`devilry.apps.core.models.Node`).
        """
        node = cls.get(user, id)
        node.short_name = short_name
        node.long_name = long_name
        cls._set_parentnode_from_id(node, parentnode_id)
        node.full_clean()
        node.save()
        return node

    @classmethod
    def delete(cls, user, id):
        """ Delete the node with the given id. """
        node = cls.get(user, id)
        node.delete()

    @classmethod
    def search(cls, user, parentnode_id="DO_NOT_FILTER", **standard_opts):
        """
        Search all nodes where the given ``user`` is admin (or all nodes if the
        user is superadmin).

        :param parentnode_id: Must be a number, ``None`` or ``"DO_NOT_FILTER"``.
            If it is a number, only return childnodes of the node with that
            id. If it is ``None``, only return top-level nodes (nodes with
            no parent). If it is ``"DO_NOT_FILTER"``, all nodes are queried.
        """
        fields = ['id', 'short_name', 'long_name']
        queryfields = ['short_name', 'long_name']
        qryset = models.Node.where_is_admin_or_superadmin(user)
        if parentnode_id != "DO_NOT_FILTER":
            qryset = qryset.filter(parentnode__id = parentnode_id)
        result = GetQryResult(fields, queryfields, qryset)
        result._standard_operations(**standard_opts)
        return result
