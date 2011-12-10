from devilry.apps.core.models.node import Node
from devilry.apps.coredao_djangoorm.nodeadmin_required import nodeadmin_required
from devilry.utils.dictutils import todict




class NodeDao(object):
    def _todict(self, node):
        return todict(node, 'id', 'short_name', 'long_name', 'etag', 'parentnode_id')

    def read(self, user, id):
        nodeadmin_required(user, "Must be admin on a node to view it.", id)
        return self._todict(Node.objects.get(pk=id))

    def update(self, user, id, short_name, long_name, parentnode_id=None):
        node = self.read(id)
        nodeadmin_required(user, "Must be admin on the current parentnode and the new parentnode to update a node.", node.parentnode_id, parentnode_id)
        node.short_name = short_name
        node.long_name = long_name
        node.parentnode_id = parentnode_id
        node.save()
        return self._todict(node)

    def create(self, user, short_name, long_name, parentnode_id=None):
        nodeadmin_required(user, "Must be admin on the parentnode to create a Node.", parentnode_id)
        node = Node(short_name=short_name, long_name=long_name, parentnode_id=parentnode_id)
        node.save()
        return self._todict(node)

    def delete(self, user, id):
        node = Node.objects.get(pk=id)
        nodeadmin_required(user, "Must be admin on parentnode to delete a Node.", node.parentnode_id)
        node.delete()

    def list(self, user, parentnode_id):
        nodeadmin_required(user, "Must be admin on a node to list its content.", parentnode_id)
        return [self._todict(node) for node in Node.object.filter(parentnode=parentnode_id)]