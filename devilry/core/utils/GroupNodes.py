from devilry.core.utils import OrderedDict


def group_assignmentgroups(assignment_groups):
    return group_nodes(assignment_groups, 2)

def group_assignments(assignments):
    return group_nodes(assignments, 1)


def group_nodes(nodes, tree_height):

    dict = OrderedDict()

    for node in nodes:
        list = make_node_list(Node(node), tree_height)
        
        if not dict.has_key(list.get_name()):
            dict[list.get_name()] = list
        else:
            dict[list.get_name()].merge(list)

    return dict.itervalues()


def make_node_list(child_node, list_count):
    
    parent = Node(child_node.node.parentnode) 
    parent.add_child(child_node)

    if list_count == 0:
        return parent
    else:
        list_count -= 1
        return make_node_list(parent, list_count)


class Node(object):

    def __init__(self, node):
        self.children = OrderedDict()
        self.node = node
            
    def __unicode__(self):
        
        if hasattr(self.node, 'long_name'):
            return self.node.long_name
        else:
            return self.node.__unicode__()

    def get_name(self):
        return self.__unicode__()

    def add_child(self, child_node):
        
        if not hasattr(child_node.node, 'short_name'):
            self.children[child_node] = child_node
        else:
            if not self.children.has_key(child_node.get_name()):
                self.children[child_node.get_name()] = child_node
            else:
                self.children[child_node.get_name()].merge(child_node)

    def merge(self, list):
        for n in list:
            self.add_child(n)

    def __iter__(self):
        return iter(self.children.values())

def print_tree(node):
    for child in node:
         print child.get_name()
         print_tree(child)
