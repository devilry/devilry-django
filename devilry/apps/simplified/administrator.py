from ..core import models
from base import GetQryResult, SimplifiedBase


class Node(SimplifiedBase):
    #default_orderby = 

    @classmethod
    def getqry(cls, user, **standard_opts):
        fields = ['id', 'short_name', 'long_name']
        queryfields = ['short_name', 'long_name']
        qryset = models.Node.where_is_admin_or_superadmin(user)
        result = GetQryResult(fields, queryfields, qryset)
        result._standard_operations(**standard_opts)
        return result

    @classmethod
    def replaceitem(cls, user, id, **kwargs):
        node = models.Node.object.get(id=id)
        #node = models.Node(**kwargs)
        node.save()

    @classmethod
    def createitem(cls, user, **kwargs):
        pass

    @classmethod
    def deleteitem(cls, id):
        pass
