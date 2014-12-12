from devilry.apps.core.models.node import Node
from devilry.apps.coredao.djangoorm.nodeadmin_required import nodeadmin_required
from devilry.apps.coredao.errors import  NotPermittedToDeleteNonEmptyError
from devilry.utils.dictutils import todict





class NodeDao(object):
    def _todict(self, node):
        return todict(node, 'id', 'short_name', 'long_name', 'parentnode_id')

    def _read(self, id):
        return Node.objects.get(pk=id)

    def read(self, user, id):
        nodeadmin_required(user, "Must be admin on a node to view it.", id)
        return self._todict(self._read(id))

    def update(self, user, id, short_name, long_name, parentnode_id=None):
        node = self._read(id)
        nodeadmin_required(user, "Must be admin on the current parentnode and the new parentnode to update a node.",
                           node.parentnode_id, parentnode_id)
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

    def _is_empty(self, node):
        return (node.child_nodes.count() + node.subjects.count()) == 0

    def delete(self, user, id):
        node = Node.objects.get(pk=id)
        nodeadmin_required(user, "Must be admin on parentnode to delete a Node.", node.parentnode_id)
        if not user.is_superuser and not self._is_empty(node):
            raise NotPermittedToDeleteNonEmptyError("Must be superuser to delete a node containing childnodes or subjects.")
        node.delete()

    def list(self, user, id):
        nodeadmin_required(user, "Must be admin on a node to list its content.", id)
        return [self._todict(node) for node in Node.objects.filter(parentnode=id)]