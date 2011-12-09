from devilry.apps.coredao.active import NodeDao
from devilry.apps.core.models.node import Node
from devilry.rest.utils import subdict, todict, force_paramtypes
from devilry.rest.restbase import RestBase


class RestNode(RestBase):
    read_fields = "id", "short_name", "long_name", "etag", "parentnode_id"

    def __init__(self, apipath, apiversion, nodedaocls=NodeDao):
        super(RestNode, self).__init__(apipath, apiversion)
        self.nodedao = nodedaocls()

    def fromdict(self, dct):
        return Node(subdict(dct, *self.read_fields))

    def todict(self, node):
        return todict(node, *self.read_fields)

    @force_paramtypes(id=int)
    def read(self, id):
        return self.todict(self.nodedao.read(id))

    def create(self, short_name, long_name):
        return self.todict(self.nodedao.create(short_name, long_name))

    @force_paramtypes(id=int)
    def update(self, id, short_name, long_name):
        return self.todict(self.nodedao.update(id, short_name, long_name))

    @force_paramtypes(parentnode_id=int)
    def list(self, parentnode_id=None):
        items = self.get_items(parentnode_id)
        return dict(
            params=dict(
                parentnode_id=parentnode_id
            ),
            links=self.get_links(),
            items=items,
            total=len(items)
        )

    def batch(self, create=[], update=[], delete=[]):
        for kw in create:
            self.create(**kw)
        for kw in update:
            self.update(**kw)
        for kw in delete:
            self.delete(**kw)

    def get_items(self, parentnode_id):
        return [self.todict(item) for item in self.nodedao.list(parentnode_id)]

    def get_links(self):
        return dict(
            admins="http://admins...."
        )