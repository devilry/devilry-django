from devilry.apps.coredao.active import NodeDao
from devilry.apps.core.models.node import Node
from devilry.rest.indata import indata
from devilry.rest.utils import subdict, todict
from devilry.rest.restbase import RestBase


class RestNode(RestBase):

    def __init__(self, nodedaocls=NodeDao, **basekwargs):
        super(RestNode, self).__init__(**basekwargs)
        self.nodedao = nodedaocls()

    def todict(self, node):
        item = node
        links = {}
        links['toplevel-nodes'] = self.geturl()
        if node['parentnode_id'] != None:
            links['parentnode'] = self.geturl(node['parentnode_id'])
        links['childnodes'] = self.geturl(params={'id': node['id']})
        links['node'] = self.geturl(node['id'])
        return dict(
            item=item,
            links=links
        )

    @indata(id=int)
    def read(self, id):
        return self.todict(self.nodedao.read(self.user, id))

    @indata(short_name=unicode, long_name=unicode)
    def create(self, short_name, long_name):
        return self.todict(self.nodedao.create(self.user, short_name, long_name))

    @indata(id=int, short_name=unicode, long_name=unicode)
    def update(self, id, short_name, long_name):
        return self.todict(self.nodedao.update(self.user, id, short_name, long_name))

    @indata(id=int)
    def list(self, id=None):
        items = self._get_items(id)
        return dict(
            params=dict(
                parentnode_id=id
            ),
            links=self.get_links(id),
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

    def _get_items(self, parentnode_id):
        return [self.todict(item) for item in self.nodedao.list(self.user, parentnode_id)]

    def get_links(self, id):
        links = {}
        if id:
            links['node'] = self.geturl(id)
        return links