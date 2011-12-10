from devilry.apps.coredao.active import NodeDao
from devilry.apps.core.models.node import Node
from devilry.rest.indata import indata
from devilry.rest.utils import subdict, todict
from devilry.rest.restbase import RestBase


class RestNode(RestBase):
    read_fields = "id", "short_name", "long_name", "etag", "parentnode_id"

    def __init__(self, apipath, apiversion, nodedaocls=NodeDao, **basekwargs):
        super(RestNode, self).__init__(apipath, apiversion, **basekwargs)
        self.nodedao = nodedaocls()

    def fromdict(self, dct):
        return Node(subdict(dct, *self.read_fields))

    def todict(self, node):
        item = todict(node, *self.read_fields)
        links = {}
        if node.parentnode_id != None:
            links['parentnode'] = self.geturl(node.parentnode_id)
        links['childnodes'] = self.geturl(params={'parentnode_id': node.id})
        links['item'] = self.geturl(node.id)
        return dict(
            item=item,
            links=links
        )

    @indata(id=int)
    def read(self, id):
        return self.todict(self.nodedao.read(id))

    @indata(short_name=unicode, long_name=unicode)
    def create(self, short_name, long_name):
        return self.todict(self.nodedao.create(short_name, long_name))

    @indata(id=int, short_name=unicode, long_name=unicode)
    def update(self, id, short_name, long_name):
        return self.todict(self.nodedao.update(id, short_name, long_name))

    @indata(parentnode_id=int)
    def list(self, parentnode_id=None):
        items = self.get_items(parentnode_id)
        return dict(
            params=dict(
                parentnode_id=parentnode_id
            ),
            links=self.get_links(parentnode_id),
            items=items,
            total=len(items)
        )

    #    @indata(parentnode_id=force_list)
    def batch(self, create=[], update=[], delete=[]):
        for kw in create:
            self.create(**kw)
        for kw in update:
            self.update(**kw)
        for kw in delete:
            self.delete(**kw)

    def get_items(self, parentnode_id):
        return [self.todict(item) for item in self.nodedao.list(parentnode_id)]

    def get_links(self, parentnode_id):
        links = {}
        if parentnode_id:
            links['parentnode'] = self.geturl(parentnode_id)
        return links