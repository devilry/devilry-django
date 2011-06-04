from ..core import models
from base import GetQryResult, SimplifiedBase
from exceptions import PermissionDeniedException


class Node(SimplifiedBase):
    #default_orderby = 

    @classmethod
    def _authorize(cls, user, node):
        if not node.can_save(user):
            raise PermissionDeniedException()

    @classmethod
    def _set_parentnode_from_id(cls, node, parentnode_id):
        if parentnode_id == None:
            node.parentnode = None
        else:
            node.parentnode = models.Node.objects.get(id=parentnode_id)

    @classmethod
    def search(cls, user, **standard_opts):
        fields = ['id', 'short_name', 'long_name']
        queryfields = ['short_name', 'long_name']
        qryset = models.Node.where_is_admin_or_superadmin(user)
        result = GetQryResult(fields, queryfields, qryset)
        result._standard_operations(**standard_opts)
        return result

    @classmethod
    def get(cls, user, id):
        node = models.Node.objects.get(id=id)
        cls._authorize(user, node)
        return node

    @classmethod
    def update(cls, user, id, short_name, long_name,
            parentnode_id=None):
        """ Update the data in the :class:`devilry.apps.core.models.Node`
        with the given ``id``.

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
    def create(cls, user, short_name, long_name, parentnode_id=None):
        """ Create a :class:`devilry.apps.core.models.Node`. """
        node =  models.Node(short_name=short_name, long_name=long_name)
        cls._set_parentnode_from_id(node, parentnode_id)
        cls._authorize(user, node) # Important that this is after parentnode is set, or admins on parentnode will not be permitted!
        node.full_clean()
        node.save()
        return node

    @classmethod
    def delete(cls, user, id):
        node = cls.get(user, id)
        node.delete()
