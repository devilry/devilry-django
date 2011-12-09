from devilry.apps.coredao.active import NodeDao
from devilry.apps.core.models.node import Node
from devilry.rest.utils import subdict, todict, force_paramtypes, indata
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

    def to_listingdict(self, node):
        item = self.todict(node)
        return dict(
            item=item,
            url=self.geturl(node.id)
        )

    def to_singledict(self, node):
        item = self.todict(node)

        urls = {}
        if node.parentnode_id != None:
            urls['parentnode'] = self.geturl(node.parentnode_id)
        urls['childnodes'] = self.geturl(params={'parentnode_id': node.id})
        return dict(
            item=item,
            urls=urls
        )

    @indata(id=int, stuff=int, saker=str, ting=unicode)
    def read(self, id, stuff=10, saker=20, ting=None):
        return self.to_singledict(self.nodedao.read(id))

    @indata(short_name=unicode, long_name=unicode)
    def create(self, short_name, long_name):
        return self.to_singledict(self.nodedao.create(short_name, long_name))

    @indata(id=int, short_name=unicode, long_name=unicode)
    def update(self, id, short_name, long_name):
        return self.to_singledict(self.nodedao.update(id, short_name, long_name))

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
        return [self.to_listingdict(item) for item in self.nodedao.list(parentnode_id)]

    def get_links(self, parentnode_id):
        links = {}
        if parentnode_id:
            links['parentnode'] = self.geturl(parentnode_id)
        return links