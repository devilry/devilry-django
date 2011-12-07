from devilry.apps.core.dao import NodeDao
from devilry.apps.core.models.node import Node
from devilry.rest.utils import subdict, todict, force_paramtypes
from devilry.rest.restbase import RestBase


class RestNode(RestBase):
    read_fields = "id", "short_name", "long_name", "etag"

    def __init__(self, nodedaocls=NodeDao):
        self.nodedao = nodedaocls()

    def fromdict(self, dct):
        return Node(subdict(dct, *self.read_fields))

    def todict(self, node):
        return todict(node, *self.read_fields)

    @force_paramtypes(id=int)
    def crud_read(self, id):
        return self.todict(self.nodedao.read(id))

    def crud_create(self, short_name, long_name):
        return self.todict(self.nodedao.create(short_name, long_name))

    @force_paramtypes(id=int)
    def crud_update(self, id, short_name, long_name):
        return self.todict(self.nodedao.update(id, short_name, long_name))

#    @force_paramtypes(parentnode=int)
    def crud_list(self, parentnode=None):
        items = self.get_items(parentnode)
        return dict(
            links=self.get_links(),
            items=items,
            total=len(items)
        )

    def get_items(self, parentnode):
        return [self.todict(item) for item in self.nodedao.list(parentnode)]

    def get_links(self):
        return dict(
            admins="http://admins...."
        )