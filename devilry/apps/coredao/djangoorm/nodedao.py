from devilry.apps.core.models.node import Node
from devilry.utils.dictutils import todict

class NodeDao(object):
    def _todict(self, node):
        return todict(node, 'id', 'short_name', 'long_name', 'etag', 'parentnode_id')

    def read(self, id):
        return self._todict(Node.objects.get(pk=id))

    def update(self, id, short_name, long_name):
        node = self.read(id)
        node.short_name = short_name
        node.long_name = long_name
        node.save()
        return self._todict(node)

    def create(self, short_name, long_name):
        node = Node(short_name=short_name, long_name=long_name)
        node.save()
        return self._todict(node)

    def delete(self, id):
        node = Node.objects.get(pk=id)
        node.delete()

    def list(self, parentnode):
        return [self._todict(node) for node in Node.objects.filter(parentnode=parentnode)]