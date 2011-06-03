from ..core import models
from base import GetQryResult, SimplifiedBase


class Node(SimplifiedBase):

    @classmethod
    def getqry(cls, user, **standard_opts):
        fields = ['id', 'short_name', 'long_name']
        queryfields = ['short_name', 'long_name']
        qryset = models.Subject.published_where_is_examiner(user)
        result = GetQryResult(fields, queryfields, qryset)
        result._standard_operations(**standard_opts)
        return result

    @classmethod
    def putitem(cls, user):
        pass

    @classmethod
    def postitem(cls, user):
        pass

    @classmethod
    def deleteitem(cls, user):
        pass
