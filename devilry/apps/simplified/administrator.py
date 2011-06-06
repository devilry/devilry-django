from ..core import models
from getqryresult import GetQryResult
from simplified_api import simplified_api
from exceptions import PermissionDenied



@simplified_api
class Node:
    """ Facade to simplify administrator actions on
    :class:`devilry.apps.core.models.Node`. """
    #CORE_MODEL = models.Node

    class Meta:
        model = models.Node

    @classmethod
    def _authorize(cls, user, node):
        if not node.can_save(user):
            raise PermissionDenied()

    #@classmethod
    #def _set_parentnode_from_id(cls, node, parentnode_id):
        #if parentnode_id == None:
            #node.parentnode = None
        #else:
            #node.parentnode = models.Node.objects.get(id=parentnode_id)

    #@classmethod
    #def create(cls, user, short_name, long_name, parentnode_id=None):
        #""" Create a node. """
        #node =  models.Node(short_name=short_name, long_name=long_name)
        #cls._set_parentnode_from_id(node, parentnode_id)
        #cls._authorize(user, node) # Important that this is after parentnode is set, or admins on parentnode will not be permitted!
        #node.full_clean()
        #node.save()
        #return node

    #@classmethod
    #def get(cls, user, id):
        #node = models.Node.objects.get(id=id)
        #cls._authorize(user, node)
        #return node

    #@classmethod
    #def update(cls, user, id, short_name, long_name,
            #parentnode_id=None):
        #""" Update the data in the node with the given ``id``.

        #:throws devilry.apps.core.models.Node.DoesNotExist:
            #If the node with ``id`` does not exists, or if
            #parentnode is not None, and no node with ``id==parentnode_id``
            #exists.
        #:throws django.core.exceptions.ValidationError:
            #If the parameters do not validate (see
            #:class:`devilry.apps.core.models.Node`).
        #"""
        #node = cls.get(user, id)
        #node.short_name = short_name
        #node.long_name = long_name
        #cls._set_parentnode_from_id(node, parentnode_id)
        #node.full_clean()
        #node.save()
        #return node

    #@classmethod
    #def delete(cls, user, id):
        #""" Delete the node with the given id. """
        #node = cls.get(user, id)
        #node.delete()

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
