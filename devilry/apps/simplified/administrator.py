from ..core import models
from base import GetQryResult, SimplifiedBase


class Node(SimplifiedBase):
    #default_orderby = 

    @classmethod
    def getqry(cls, user, **standard_opts):
    #def search(cls, user, **standard_opts):
        fields = ['id', 'short_name', 'long_name']
        queryfields = ['short_name', 'long_name']
        qryset = models.Node.where_is_admin_or_superadmin(user)
        result = GetQryResult(fields, queryfields, qryset)
        result._standard_operations(**standard_opts)
        return result

    @classmethod
    def replaceitem(cls, user, id, short_name=None, long_name=None,
            parentnode_id=None):
        node = models.Node.objects.get(id=id)
        node.short_name = short_name
        node.long_name = long_name
        if parentnode_id != None:
            node.parentnode = models.Node.objects.get(id=parentnode_id)
        node.save()
        return node

    @classmethod
    def createitem(cls, user, **kwargs):
        pass

    @classmethod
    def getitem(cls, id):
        pass

    @classmethod
    def deleteitem(cls, id):
        pass
